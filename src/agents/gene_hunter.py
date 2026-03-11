"""Gene Hunter agent: identifies disease-associated gene targets."""

import httpx
from google import genai

from src.models import GeneAssociation
from src.tools.open_targets import search_disease, get_disease_targets

SYSTEM_PROMPT = """You are a computational biology expert specializing in target identification.
You are given gene-disease association results from Open Targets Platform.
Your job is to evaluate whether the results are sufficient or if the query should be refined.

If the results look reasonable (multiple genes with meaningful association scores), say "PROCEED".
If the disease name may need synonyms or the results are sparse, suggest a refined query.

Respond concisely."""


async def call_llm(prompt: str, system: str = SYSTEM_PROMPT) -> str:
    """Call the LLM for reasoning. Separated for testability."""
    client = genai.Client()
    response = await client.aio.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=genai.types.GenerateContentConfig(
            system_instruction=system,
        ),
    )
    return response.text or ""


async def run_gene_hunter(
    client: httpx.AsyncClient,
    disease_name: str,
    *,
    top_n: int = 10,
) -> list[GeneAssociation]:
    """Identify gene targets for a disease using Open Targets.

    Returns a list of GeneAssociation models ranked by association score.
    """
    # Step 1: Resolve disease name to EFO ID
    disease = await search_disease(client, disease_name)
    if disease is None:
        raise ValueError(f"Could not find disease '{disease_name}' in Open Targets")

    # Step 2: Get associated targets
    raw_targets = await get_disease_targets(client, disease["id"], top_n=top_n)
    if not raw_targets:
        raise ValueError(f"No gene associations found for {disease['name']}")

    # Step 3: LLM evaluates results
    summary = "\n".join(
        f"- {t['gene_symbol']} ({t['target_name']}): score={t['association_score']:.3f}"
        for t in raw_targets
    )
    prompt = f"Disease: {disease['name']}\nTop {len(raw_targets)} associated genes:\n{summary}\n\nAre these results sufficient for a drug target analysis?"
    await call_llm(prompt)

    # Step 4: Convert to models
    return [
        GeneAssociation(
            gene_symbol=t["gene_symbol"],
            ensembl_id=t["ensembl_id"],
            association_score=t["association_score"],
            target_name=t["target_name"],
            datatype_scores=t.get("datatype_scores", {}),
        )
        for t in raw_targets
    ]
