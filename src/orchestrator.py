"""Orchestrator: coordinates the multi-agent drug target reconnaissance pipeline."""

import asyncio
import os
import sys

import httpx
from google import genai
from dotenv import load_dotenv

from src.agents.druggability import run_druggability_assessor
from src.agents.gene_hunter import run_gene_hunter
from src.agents.literature import run_literature_validator
from src.models import ReconReport, TargetReport

load_dotenv()

SYSTEM_PROMPT = """You are a senior computational biologist synthesizing drug target findings.
Given ranked gene targets with druggability assessments and literature evidence,
write a concise recommendation section for a drug target report.

Focus on: which targets are most promising and why, key risks, and suggested next steps.
Be specific, cite evidence, and keep it to 3-5 sentences."""


async def call_llm(prompt: str, system: str = SYSTEM_PROMPT) -> str:
    """Call the LLM for final synthesis."""
    client = genai.Client()
    response = await client.aio.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=genai.types.GenerateContentConfig(
            system_instruction=system,
        ),
    )
    return response.text or ""


async def run_recon(disease_name: str, *, top_n: int = 5) -> ReconReport:
    """Run the full drug target reconnaissance pipeline.

    1. Gene Hunter identifies associated targets
    2. Druggability + Literature agents run in parallel per gene
    3. LLM synthesizes final ranked report
    """
    async with httpx.AsyncClient(timeout=60.0) as client:
        # Step 1: Identify gene targets
        print(f"[Gene Hunter] Searching for targets associated with '{disease_name}'...")
        genes = await run_gene_hunter(client, disease_name, top_n=top_n)
        print(f"[Gene Hunter] Found {len(genes)} targets")

        # Step 2: Parallel assessment per gene
        target_reports: list[TargetReport] = []

        async def assess_gene(gene, delay=0):
            if delay:
                await asyncio.sleep(delay)
            print(f"[Assessing] {gene.gene_symbol}...")
            druggability, literature = await asyncio.gather(
                run_druggability_assessor(client, gene.gene_symbol),
                run_literature_validator(client, gene.gene_symbol, disease_name),
            )
            return gene, druggability, literature

        results = await asyncio.gather(
            *(assess_gene(gene, delay=i * 1.5) for i, gene in enumerate(genes))
        )

        for gene, druggability, literature in results:
            target_reports.append(TargetReport(
                gene_symbol=gene.gene_symbol,
                ensembl_id=gene.ensembl_id,
                target_name=gene.target_name,
                association_score=gene.association_score,
                druggability=druggability,
                literature=literature,
                reasoning="",
            ))

        # Step 3: LLM synthesizes recommendation
        summary = "\n\n".join(
            f"**{t.gene_symbol}** ({t.target_name})\n"
            f"  Association score: {t.association_score:.3f}\n"
            f"  Druggability: {t.druggability.druggability_verdict}\n"
            f"  Compounds: {t.druggability.num_known_compounds} (max phase {t.druggability.max_phase_drug})\n"
            f"  Literature: {t.literature.num_recent_papers} papers, {t.literature.support_level}\n"
            f"  Key findings: {t.literature.key_findings_summary}"
            for t in target_reports
        )
        prompt = f"Disease: {disease_name}\n\nTarget summaries:\n{summary}\n\nWrite the recommendation."
        recommendation = await call_llm(prompt)

        return ReconReport(
            disease=disease_name,
            disease_id=genes[0].ensembl_id if genes else "",
            targets=target_reports,
            recommendation=recommendation,
        )


def format_report_markdown(report: ReconReport) -> str:
    """Format a ReconReport as readable Markdown."""
    lines = [
        f"# Drug Target Reconnaissance: {report.disease}",
        "",
        f"**Disease ID:** {report.disease_id}",
        f"**Targets analyzed:** {len(report.targets)}",
        "",
        "---",
        "",
    ]

    for i, t in enumerate(report.targets, 1):
        lines.extend([
            f"## {i}. {t.gene_symbol} — {t.target_name}",
            "",
            "| Metric | Value |",
            "|--------|-------|",
            f"| Association Score | {t.association_score:.3f} |",
            f"| UniProt Accession | {t.druggability.uniprot_accession} |",
            f"| Protein Class | {t.druggability.protein_class} |",
            f"| 3D Structure | {'Yes' if t.druggability.has_3d_structure else 'No'} |",
            f"| Known Compounds | {t.druggability.num_known_compounds} |",
            f"| Max Drug Phase | {t.druggability.max_phase_drug} |",
            f"| PubMed Papers | {t.literature.num_recent_papers} |",
            f"| Evidence | {t.literature.support_level} |",
            "",
            f"**Druggability:** {t.druggability.druggability_verdict}",
            "",
            f"**Literature:** {t.literature.key_findings_summary}",
            "",
            f"**PMIDs:** {', '.join(t.literature.top_pmids)}",
            "",
            "---",
            "",
        ])

    lines.extend([
        "## Recommendation",
        "",
        report.recommendation,
    ])

    return "\n".join(lines)


async def main():
    """CLI entry point."""
    disease = sys.argv[1] if len(sys.argv) > 1 else "Alzheimer disease"
    top_n = int(sys.argv[2]) if len(sys.argv) > 2 else 5

    report = await run_recon(disease, top_n=top_n)

    # Output Markdown
    md = format_report_markdown(report)
    print(md)

    # Save outputs
    import json
    import re
    slug = re.sub(r"[^a-z0-9]+", "-", disease.lower()).strip("-")
    os.makedirs("reports", exist_ok=True)
    json_path = f"reports/report-{slug}.json"
    md_path = f"reports/report-{slug}.md"
    with open(json_path, "w") as f:
        json.dump(report.model_dump(), f, indent=2)
    with open(md_path, "w") as f:
        f.write(md)
    print(f"\nSaved {json_path} and {md_path}")


if __name__ == "__main__":
    asyncio.run(main())
