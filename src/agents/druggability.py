"""Druggability Assessor agent: evaluates target tractability."""

import httpx
from google import genai

from src.models import DruggabilityProfile
from src.tools.uniprot import fetch_protein_info
from src.tools.chembl import get_target_by_uniprot, assess_compounds

SYSTEM_PROMPT = """You are a medicinal chemistry expert assessing drug target tractability.
Given protein annotation (from UniProt) and compound data (from ChEMBL), provide a brief
druggability verdict. Consider:
- Protein class and family (enzymes/receptors are more druggable)
- Subcellular location (extracellular/membrane proteins are easier to target)
- Existing 3D structures (enables structure-based drug design)
- Known bioactive compounds and their clinical progress

Respond with a 1-2 sentence druggability verdict."""


async def call_llm(prompt: str, system: str = SYSTEM_PROMPT) -> str:
    """Call the LLM for druggability reasoning."""
    client = genai.Client()
    response = await client.aio.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=genai.types.GenerateContentConfig(
            system_instruction=system,
        ),
    )
    return response.text or ""


async def run_druggability_assessor(
    client: httpx.AsyncClient, gene_symbol: str
) -> DruggabilityProfile:
    """Assess druggability for a single gene target.

    Queries UniProt for protein info and ChEMBL for compound landscape.
    """
    # Step 1: Get protein info from UniProt
    protein = await fetch_protein_info(client, gene_symbol)
    accession = protein["accession"] if protein else ""
    pdb_ids = protein["pdb_ids"] if protein else []
    locations = protein["subcellular_locations"] if protein else []
    families = protein["protein_families"] if protein else []
    function_text = protein["function"] if protein else ""

    # Step 2: Get compound data from ChEMBL
    compounds_data = {"num_compounds": 0, "max_phase": 0, "top_compounds": []}
    if accession:
        target = await get_target_by_uniprot(client, accession)
        if target:
            compounds_data = await assess_compounds(client, target["target_chembl_id"])

    # Step 3: LLM interprets the data
    prompt = f"""Gene: {gene_symbol}
UniProt accession: {accession}
Protein families: {families}
Subcellular location: {locations}
Function: {function_text}
3D structures (PDB): {len(pdb_ids)} structures
Known compounds: {compounds_data['num_compounds']}
Max clinical phase: {compounds_data['max_phase']}
Top compounds: {compounds_data['top_compounds'][:5]}

Assess the druggability of this target."""

    verdict = await call_llm(prompt)

    return DruggabilityProfile(
        gene_symbol=gene_symbol,
        uniprot_accession=accession,
        protein_class=families[0] if families else "Unknown",
        subcellular_locations=locations,
        has_3d_structure=len(pdb_ids) > 0,
        num_known_compounds=compounds_data["num_compounds"],
        max_phase_drug=compounds_data["max_phase"],
        top_compounds=compounds_data["top_compounds"][:5],
        druggability_verdict=verdict,
    )
