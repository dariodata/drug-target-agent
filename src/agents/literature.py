"""Literature Validator agent: validates gene-disease links via PubMed."""

import json as json_mod
import httpx
from google import genai

from src.models import LiteratureEvidence
from src.tools.pubmed import search_papers, fetch_abstracts

SYSTEM_PROMPT = """You are a biomedical literature analyst. Given PubMed abstracts about a gene-disease pair,
classify the overall evidence and summarize key findings.

Respond in JSON format:
{
  "support_level": "supporting" | "contradicting" | "inconclusive",
  "key_findings": "2-3 sentence summary of the main findings"
}"""


async def call_llm(prompt: str, system: str = SYSTEM_PROMPT) -> str:
    """Call the LLM for literature analysis."""
    client = genai.Client()
    response = await client.aio.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=genai.types.GenerateContentConfig(
            system_instruction=system,
        ),
    )
    return response.text or ""


async def run_literature_validator(
    client: httpx.AsyncClient,
    gene_symbol: str,
    disease: str,
    *,
    max_papers: int = 5,
) -> LiteratureEvidence:
    """Validate a gene-disease association through PubMed literature.

    Searches for papers, fetches abstracts, and uses LLM to classify evidence.
    """
    # Step 1: Search PubMed
    pmids, total_count = await search_papers(
        client, gene_symbol, disease, max_results=max_papers
    )

    # Step 2: Fetch abstracts
    articles = []
    if pmids:
        articles = await fetch_abstracts(client, pmids)

    # Step 3: LLM classifies evidence
    if articles:
        abstracts_text = "\n\n".join(
            f"PMID {a['pmid']}: {a['title']}\n{a['abstract']}"
            for a in articles
        )
        prompt = f"Gene: {gene_symbol}\nDisease: {disease}\n\nAbstracts:\n{abstracts_text}\n\nClassify the evidence."
        llm_response = await call_llm(prompt)
        try:
            parsed = json_mod.loads(llm_response)
            support_level = parsed.get("support_level", "inconclusive")
            key_findings = parsed.get("key_findings", "")
        except json_mod.JSONDecodeError:
            support_level = "inconclusive"
            key_findings = llm_response
    else:
        support_level = "inconclusive"
        key_findings = "No papers found for this gene-disease pair."

    return LiteratureEvidence(
        gene_symbol=gene_symbol,
        disease=disease,
        num_recent_papers=total_count,
        key_findings_summary=key_findings,
        support_level=support_level,
        top_pmids=pmids[:3],
    )
