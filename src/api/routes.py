"""FastAPI route definitions for the drug target explorer API."""

from fastapi import APIRouter, HTTPException, Query

from src.api.neo4j_client import query, query_single

router = APIRouter(prefix="/api")


@router.get("/stats")
async def get_stats():
    """Aggregate counts across the knowledge graph."""
    results = await query(
        """OPTIONAL MATCH (d:Disease) WITH count(d) AS diseases
           OPTIONAL MATCH (g:Gene) WITH diseases, count(g) AS genes
           OPTIONAL MATCH (p:Protein) WITH diseases, genes, count(p) AS proteins
           OPTIONAL MATCH (c:Compound) WITH diseases, genes, proteins, count(c) AS compounds
           OPTIONAL MATCH (pa:Paper) WITH diseases, genes, proteins, compounds, count(pa) AS papers
           OPTIONAL MATCH (pw:Pathway) WITH diseases, genes, proteins, compounds, papers, count(pw) AS pathways
           RETURN diseases, genes, proteins, compounds, papers, pathways"""
    )
    if results:
        return results[0]
    return {"diseases": 0, "genes": 0, "proteins": 0, "compounds": 0, "papers": 0, "pathways": 0}


@router.get("/diseases")
async def list_diseases():
    """List all diseases with target counts."""
    return await query(
        """MATCH (d:Disease)
           OPTIONAL MATCH (d)-[:ASSOCIATED_WITH]->(g:Gene)
           RETURN d.efo_id AS efo_id, d.name AS name, count(g) AS target_count
           ORDER BY d.name"""
    )


@router.get("/diseases/{efo_id}")
async def get_disease(efo_id: str):
    """Full disease report data including all targets."""
    disease = await query_single(
        "MATCH (d:Disease {efo_id: $efo_id}) RETURN d.efo_id AS efo_id, d.name AS name",
        efo_id=efo_id,
    )
    if not disease:
        raise HTTPException(status_code=404, detail="Disease not found")

    targets = await query(
        """MATCH (d:Disease {efo_id: $efo_id})-[a:ASSOCIATED_WITH]->(g:Gene)
           OPTIONAL MATCH (g)-[:ENCODES]->(p:Protein)
           OPTIONAL MATCH (p)-[:HAS_COMPOUND]->(c:Compound)
           OPTIONAL MATCH (g)-[:MENTIONED_IN]->(pa:Paper)
           OPTIONAL MATCH (g)-[:INVOLVED_IN]->(pw:Pathway)
           WITH g, a, p,
                collect(DISTINCT {chembl_id: c.chembl_id, pref_name: c.pref_name, max_phase: c.max_phase}) AS compounds,
                collect(DISTINCT pa.pmid) AS pmids,
                collect(DISTINCT {reactome_id: pw.reactome_id, name: pw.name}) AS pathways
           RETURN g.ensembl_id AS ensembl_id,
                  g.symbol AS gene_symbol,
                  g.name AS target_name,
                  a.score AS association_score,
                  p.uniprot_acc AS uniprot_accession,
                  p.protein_class AS protein_class,
                  p.subcellular_locations AS subcellular_locations,
                  p.has_3d_structure AS has_3d_structure,
                  compounds,
                  pmids,
                  pathways
           ORDER BY a.score DESC""",
        efo_id=efo_id,
    )

    # Filter out null entries from optional matches
    for t in targets:
        t["compounds"] = [c for c in t["compounds"] if c.get("chembl_id")]
        t["pmids"] = [p for p in t["pmids"] if p]
        t["pathways"] = [p for p in t["pathways"] if p.get("reactome_id")]

    return {**disease, "targets": targets}


@router.get("/graph")
async def get_full_graph():
    """Full graph data formatted for Cytoscape.js."""
    return await _build_graph_data()


@router.get("/graph/{efo_id}")
async def get_disease_graph(efo_id: str):
    """Subgraph for a single disease, formatted for Cytoscape.js."""
    disease = await query_single(
        "MATCH (d:Disease {efo_id: $efo_id}) RETURN d.efo_id AS efo_id",
        efo_id=efo_id,
    )
    if not disease:
        raise HTTPException(status_code=404, detail="Disease not found")
    return await _build_graph_data(efo_id=efo_id)


async def _build_graph_data(efo_id: str | None = None) -> dict:
    """Build Cytoscape.js-compatible graph JSON (nodes + edges).

    If efo_id is provided, returns only the subgraph for that disease.
    """
    nodes = []
    edges = []

    # Disease filter clause
    if efo_id:
        disease_match = "MATCH (d:Disease {efo_id: $efo_id})"
        params = {"efo_id": efo_id}
    else:
        disease_match = "MATCH (d:Disease)"
        params = {}

    # Diseases
    diseases = await query(
        f"{disease_match} RETURN d.efo_id AS id, d.name AS name",
        **params,
    )
    for d in diseases:
        nodes.append({"data": {"id": d["id"], "label": d["name"], "type": "disease"}})

    # Genes + ASSOCIATED_WITH edges
    genes = await query(
        f"""{disease_match}-[a:ASSOCIATED_WITH]->(g:Gene)
            RETURN DISTINCT g.ensembl_id AS id, g.symbol AS symbol, g.name AS name,
                   d.efo_id AS disease_id, a.score AS score""",
        **params,
    )
    seen_genes = set()
    for g in genes:
        if g["id"] not in seen_genes:
            nodes.append({"data": {"id": g["id"], "label": g["symbol"], "name": g["name"], "type": "gene"}})
            seen_genes.add(g["id"])
        edges.append({"data": {
            "source": g["disease_id"], "target": g["id"],
            "label": "ASSOCIATED_WITH", "score": g["score"],
        }})

    # Proteins + ENCODES edges
    proteins = await query(
        f"""{disease_match}-[:ASSOCIATED_WITH]->(g:Gene)-[:ENCODES]->(p:Protein)
            RETURN DISTINCT p.uniprot_acc AS id, p.protein_class AS protein_class,
                   p.has_3d_structure AS has_3d, g.ensembl_id AS gene_id""",
        **params,
    )
    seen_proteins = set()
    for p in proteins:
        if p["id"] not in seen_proteins:
            nodes.append({"data": {"id": p["id"], "label": p["id"], "protein_class": p["protein_class"], "type": "protein"}})
            seen_proteins.add(p["id"])
        edges.append({"data": {"source": p["gene_id"], "target": p["id"], "label": "ENCODES"}})

    # Compounds + HAS_COMPOUND edges
    compounds = await query(
        f"""{disease_match}-[:ASSOCIATED_WITH]->(g:Gene)-[:ENCODES]->(p:Protein)-[:HAS_COMPOUND]->(c:Compound)
            RETURN DISTINCT c.chembl_id AS id, c.pref_name AS name, c.max_phase AS max_phase,
                   p.uniprot_acc AS protein_id""",
        **params,
    )
    seen_compounds = set()
    for c in compounds:
        if c["id"] not in seen_compounds:
            nodes.append({"data": {"id": c["id"], "label": c["name"] or c["id"], "max_phase": c["max_phase"], "type": "compound"}})
            seen_compounds.add(c["id"])
        edges.append({"data": {"source": c["protein_id"], "target": c["id"], "label": "HAS_COMPOUND"}})

    # Papers + MENTIONED_IN edges
    papers = await query(
        f"""{disease_match}-[:ASSOCIATED_WITH]->(g:Gene)-[m:MENTIONED_IN]->(pa:Paper)
            RETURN DISTINCT pa.pmid AS id, pa.title AS title,
                   g.ensembl_id AS gene_id, m.support_level AS support_level""",
        **params,
    )
    seen_papers = set()
    for p in papers:
        if p["id"] not in seen_papers:
            nodes.append({"data": {"id": p["id"], "label": f"PMID:{p['id']}", "title": p["title"], "type": "paper"}})
            seen_papers.add(p["id"])
        edges.append({"data": {
            "source": p["gene_id"], "target": p["id"],
            "label": "MENTIONED_IN", "support_level": p["support_level"],
        }})

    # Pathways + INVOLVED_IN edges
    pathways = await query(
        f"""{disease_match}-[:ASSOCIATED_WITH]->(g:Gene)-[:INVOLVED_IN]->(pw:Pathway)
            RETURN DISTINCT pw.reactome_id AS id, pw.name AS name,
                   g.ensembl_id AS gene_id""",
        **params,
    )
    seen_pathways = set()
    for pw in pathways:
        if pw["id"] not in seen_pathways:
            nodes.append({"data": {"id": pw["id"], "label": pw["name"], "type": "pathway"}})
            seen_pathways.add(pw["id"])
        edges.append({"data": {"source": pw["gene_id"], "target": pw["id"], "label": "INVOLVED_IN"}})

    return {"nodes": nodes, "edges": edges}


@router.get("/compare")
async def compare_diseases(
    d1: str = Query(..., description="EFO ID of first disease"),
    d2: str = Query(..., description="EFO ID of second disease"),
):
    """Find shared gene targets between two diseases."""
    shared = await query(
        """MATCH (d1:Disease {efo_id: $d1})-[a1:ASSOCIATED_WITH]->(g:Gene)<-[a2:ASSOCIATED_WITH]-(d2:Disease {efo_id: $d2})
           OPTIONAL MATCH (g)-[:ENCODES]->(p:Protein)
           OPTIONAL MATCH (g)-[:INVOLVED_IN]->(pw:Pathway)
           RETURN g.ensembl_id AS ensembl_id,
                  g.symbol AS gene_symbol,
                  g.name AS target_name,
                  a1.score AS score_d1,
                  a2.score AS score_d2,
                  p.uniprot_acc AS uniprot_accession,
                  p.protein_class AS protein_class,
                  collect(DISTINCT {reactome_id: pw.reactome_id, name: pw.name}) AS shared_pathways
           ORDER BY (a1.score + a2.score) DESC""",
        d1=d1, d2=d2,
    )

    # Filter nulls from optional pathway matches
    for s in shared:
        s["shared_pathways"] = [p for p in s["shared_pathways"] if p.get("reactome_id")]

    # Get disease names
    d1_info = await query_single("MATCH (d:Disease {efo_id: $id}) RETURN d.name AS name", id=d1)
    d2_info = await query_single("MATCH (d:Disease {efo_id: $id}) RETURN d.name AS name", id=d2)

    # Get unique targets per disease
    only_d1 = await query(
        """MATCH (d1:Disease {efo_id: $d1})-[:ASSOCIATED_WITH]->(g:Gene)
           WHERE NOT (g)<-[:ASSOCIATED_WITH]-(:Disease {efo_id: $d2})
           RETURN g.symbol AS gene_symbol, g.ensembl_id AS ensembl_id""",
        d1=d1, d2=d2,
    )
    only_d2 = await query(
        """MATCH (d2:Disease {efo_id: $d2})-[:ASSOCIATED_WITH]->(g:Gene)
           WHERE NOT (g)<-[:ASSOCIATED_WITH]-(:Disease {efo_id: $d1})
           RETURN g.symbol AS gene_symbol, g.ensembl_id AS ensembl_id""",
        d1=d1, d2=d2,
    )

    return {
        "disease_1": {"efo_id": d1, "name": d1_info["name"] if d1_info else d1},
        "disease_2": {"efo_id": d2, "name": d2_info["name"] if d2_info else d2},
        "shared_targets": shared,
        "only_in_d1": only_d1,
        "only_in_d2": only_d2,
    }


@router.get("/targets/{gene_symbol}")
async def get_target(gene_symbol: str):
    """Gene detail with all connected data."""
    gene = await query_single(
        """MATCH (g:Gene {symbol: $symbol})
           RETURN g.ensembl_id AS ensembl_id, g.symbol AS gene_symbol, g.name AS target_name""",
        symbol=gene_symbol,
    )
    if not gene:
        raise HTTPException(status_code=404, detail="Gene not found")

    # Diseases this gene is associated with
    diseases = await query(
        """MATCH (d:Disease)-[a:ASSOCIATED_WITH]->(g:Gene {symbol: $symbol})
           RETURN d.efo_id AS efo_id, d.name AS name, a.score AS score
           ORDER BY a.score DESC""",
        symbol=gene_symbol,
    )

    # Protein info
    protein = await query_single(
        """MATCH (g:Gene {symbol: $symbol})-[:ENCODES]->(p:Protein)
           RETURN p.uniprot_acc AS uniprot_accession, p.protein_class AS protein_class,
                  p.subcellular_locations AS subcellular_locations, p.has_3d_structure AS has_3d_structure""",
        symbol=gene_symbol,
    )

    # Compounds
    compounds = await query(
        """MATCH (g:Gene {symbol: $symbol})-[:ENCODES]->(p:Protein)-[:HAS_COMPOUND]->(c:Compound)
           RETURN c.chembl_id AS chembl_id, c.pref_name AS pref_name, c.max_phase AS max_phase""",
        symbol=gene_symbol,
    )

    # Papers
    papers = await query(
        """MATCH (g:Gene {symbol: $symbol})-[m:MENTIONED_IN]->(pa:Paper)
           RETURN pa.pmid AS pmid, pa.title AS title, m.support_level AS support_level""",
        symbol=gene_symbol,
    )

    # Pathways
    pathways = await query(
        """MATCH (g:Gene {symbol: $symbol})-[:INVOLVED_IN]->(pw:Pathway)
           RETURN pw.reactome_id AS reactome_id, pw.name AS name""",
        symbol=gene_symbol,
    )

    return {
        **gene,
        "diseases": diseases,
        "protein": protein,
        "compounds": compounds,
        "papers": papers,
        "pathways": pathways,
    }
