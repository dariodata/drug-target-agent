"""AlphaFold structure lookup by UniProt accession.

Returns predicted structure URL + summary confidence (pLDDT mean).
API docs: https://alphafold.ebi.ac.uk/api-docs
"""
from __future__ import annotations

import httpx
from pydantic import BaseModel, Field


class AlphaFoldStructure(BaseModel):
    """Summary of an AlphaFold-predicted structure for a UniProt entry."""

    uniprot_id: str
    pdb_url: str = Field(..., description="Direct download URL for the PDB file")
    cif_url: str = Field(..., description="Direct download URL for the mmCIF file")
    plddt_mean: float | None = Field(None, description="Mean pLDDT across the structure (0-100)")
    organism_scientific_name: str | None = None
    uniprot_description: str | None = None
    model_created_date: str | None = None


_BASE = "https://alphafold.ebi.ac.uk/api/prediction"


async def fetch_alphafold_structure(uniprot_id: str, *, timeout: float = 10.0) -> AlphaFoldStructure | None:
    """Fetch the latest AlphaFold prediction for a UniProt accession.

    Returns None if no prediction exists for this accession.
    """
    url = f"{_BASE}/{uniprot_id}"
    async with httpx.AsyncClient(timeout=timeout) as client:
        resp = await client.get(url)
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        data = resp.json()

    if not data:
        return None

    # API returns a list — take the first/latest entry.
    entry = data[0]
    return AlphaFoldStructure(
        uniprot_id=uniprot_id,
        pdb_url=entry.get("pdbUrl", ""),
        cif_url=entry.get("cifUrl", ""),
        plddt_mean=entry.get("globalMetricValue"),
        organism_scientific_name=entry.get("organismScientificName"),
        uniprot_description=entry.get("uniprotDescription"),
        model_created_date=entry.get("modelCreatedDate"),
    )


# TODO: add a `fetch_alphafold_pae` variant returning the predicted aligned error matrix
# for higher-confidence interface analysis. AlphaFold-Multimer support is a v2 concern.
