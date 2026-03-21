"""Load drug target reconnaissance reports into Neo4j.

Usage:
    uv run python -m src.neo4j_loader reports/report-huntington-disease.json
    uv run python -m src.neo4j_loader reports/  # loads all JSON reports in directory

Environment variables:
    NEO4J_URI      - Bolt URI (default: bolt://localhost:7687)
    NEO4J_USER     - Username (default: neo4j)
    NEO4J_PASSWORD - Password (required)
"""

import asyncio
import json
import os
import sys
from pathlib import Path

from neo4j import AsyncGraphDatabase

from src.models import ReconReport


def _get_driver():
    """Create an async Neo4j driver from environment variables."""
    uri = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
    user = os.environ.get("NEO4J_USER", "neo4j")
    password = os.environ.get("NEO4J_PASSWORD", "")
    if not password:
        raise ValueError("NEO4J_PASSWORD environment variable is required")
    return AsyncGraphDatabase.driver(uri, auth=(user, password))


async def create_constraints(driver) -> None:
    """Create uniqueness constraints for node types."""
    constraints = [
        "CREATE CONSTRAINT IF NOT EXISTS FOR (d:Disease) REQUIRE d.efo_id IS UNIQUE",
        "CREATE CONSTRAINT IF NOT EXISTS FOR (g:Gene) REQUIRE g.ensembl_id IS UNIQUE",
        "CREATE CONSTRAINT IF NOT EXISTS FOR (p:Protein) REQUIRE p.uniprot_acc IS UNIQUE",
        "CREATE CONSTRAINT IF NOT EXISTS FOR (c:Compound) REQUIRE c.chembl_id IS UNIQUE",
        "CREATE CONSTRAINT IF NOT EXISTS FOR (pa:Paper) REQUIRE pa.pmid IS UNIQUE",
        "CREATE CONSTRAINT IF NOT EXISTS FOR (pw:Pathway) REQUIRE pw.reactome_id IS UNIQUE",
    ]
    async with driver.session() as session:
        for cypher in constraints:
            await session.run(cypher)


async def load_report(driver, report: ReconReport) -> dict:
    """Load a single ReconReport into Neo4j. Returns counts of created entities."""
    counts = {"diseases": 0, "genes": 0, "proteins": 0, "compounds": 0,
              "papers": 0, "pathways": 0, "reports": 0}

    async with driver.session() as session:
        # Create Disease node
        await session.run(
            "MERGE (d:Disease {efo_id: $efo_id}) SET d.name = $name",
            efo_id=report.disease_id, name=report.disease,
        )
        counts["diseases"] += 1

        # Create Report node
        from datetime import date
        await session.run(
            """MERGE (r:Report {disease: $disease, date: $date})
               SET r.recommendation = $recommendation
               WITH r
               MATCH (d:Disease {efo_id: $efo_id})
               MERGE (r)-[:COVERS]->(d)""",
            disease=report.disease,
            date=str(date.today()),
            recommendation=report.recommendation,
            efo_id=report.disease_id,
        )
        counts["reports"] += 1

        for target in report.targets:
            # Gene node
            await session.run(
                """MERGE (g:Gene {ensembl_id: $ensembl_id})
                   SET g.symbol = $symbol, g.name = $name""",
                ensembl_id=target.ensembl_id,
                symbol=target.gene_symbol,
                name=target.target_name,
            )
            counts["genes"] += 1

            # Disease -[ASSOCIATED_WITH]-> Gene
            await session.run(
                """MATCH (d:Disease {efo_id: $efo_id})
                   MATCH (g:Gene {ensembl_id: $ensembl_id})
                   MERGE (d)-[r:ASSOCIATED_WITH]->(g)
                   SET r.score = $score""",
                efo_id=report.disease_id,
                ensembl_id=target.ensembl_id,
                score=target.association_score,
            )

            # Protein node + Gene -[ENCODES]-> Protein
            drug = target.druggability
            if drug.uniprot_accession:
                await session.run(
                    """MERGE (p:Protein {uniprot_acc: $acc})
                       SET p.protein_class = $pclass,
                           p.subcellular_locations = $locs,
                           p.has_3d_structure = $has3d
                       WITH p
                       MATCH (g:Gene {ensembl_id: $ensembl_id})
                       MERGE (g)-[:ENCODES]->(p)""",
                    acc=drug.uniprot_accession,
                    pclass=drug.protein_class,
                    locs=drug.subcellular_locations,
                    has3d=drug.has_3d_structure,
                    ensembl_id=target.ensembl_id,
                )
                counts["proteins"] += 1

                # Compound nodes + Protein -[HAS_COMPOUND]-> Compound
                for comp in drug.top_compounds:
                    chembl_id = comp.get("chembl_id", "")
                    if not chembl_id:
                        continue
                    await session.run(
                        """MERGE (c:Compound {chembl_id: $chembl_id})
                           SET c.pref_name = $name, c.max_phase = $phase
                           WITH c
                           MATCH (p:Protein {uniprot_acc: $acc})
                           MERGE (p)-[:HAS_COMPOUND]->(c)""",
                        chembl_id=chembl_id,
                        name=comp.get("pref_name", ""),
                        phase=comp.get("max_phase", 0),
                        acc=drug.uniprot_accession,
                    )
                    counts["compounds"] += 1

            # Paper nodes + Gene -[MENTIONED_IN]-> Paper
            lit = target.literature
            for pmid in lit.top_pmids:
                await session.run(
                    """MERGE (pa:Paper {pmid: $pmid})
                       WITH pa
                       MATCH (g:Gene {ensembl_id: $ensembl_id})
                       MERGE (g)-[r:MENTIONED_IN]->(pa)
                       SET r.support_level = $support""",
                    pmid=pmid,
                    ensembl_id=target.ensembl_id,
                    support=lit.support_level,
                )
                counts["papers"] += 1

            # Pathway nodes + Gene -[INVOLVED_IN]-> Pathway
            for pathway in target.pathways:
                await session.run(
                    """MERGE (pw:Pathway {reactome_id: $rid})
                       SET pw.name = $name
                       WITH pw
                       MATCH (g:Gene {ensembl_id: $ensembl_id})
                       MERGE (g)-[:INVOLVED_IN]->(pw)""",
                    rid=pathway.reactome_id,
                    name=pathway.name,
                    ensembl_id=target.ensembl_id,
                )
                counts["pathways"] += 1

    return counts


async def main():
    """CLI entry point: load one or more report JSON files into Neo4j."""
    if len(sys.argv) < 2:
        print("Usage: python -m src.neo4j_loader <report.json or directory>")
        sys.exit(1)

    path = Path(sys.argv[1])
    if path.is_dir():
        files = sorted(path.glob("report-*.json"))
    else:
        files = [path]

    if not files:
        print(f"No report JSON files found at {path}")
        sys.exit(1)

    driver = _get_driver()
    try:
        await create_constraints(driver)
        for f in files:
            print(f"Loading {f.name}...")
            data = json.loads(f.read_text())
            report = ReconReport(**data)
            counts = await load_report(driver, report)
            print(f"  Loaded: {counts}")
    finally:
        await driver.close()

    print("Done.")


if __name__ == "__main__":
    asyncio.run(main())
