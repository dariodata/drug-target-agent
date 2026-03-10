"""ChEMBL REST API wrapper."""

import httpx

CHEMBL_BASE = "https://www.ebi.ac.uk/chembl/api/data"


async def get_target_by_uniprot(
    client: httpx.AsyncClient, uniprot_accession: str
) -> dict | None:
    """Resolve a UniProt accession to a ChEMBL target. Returns first match or None."""
    resp = await client.get(
        f"{CHEMBL_BASE}/target.json",
        params={"target_components__accession": uniprot_accession, "limit": 1},
    )
    resp.raise_for_status()
    targets = resp.json().get("targets", [])
    return targets[0] if targets else None


async def get_activities(
    client: httpx.AsyncClient,
    target_chembl_id: str,
    *,
    limit: int = 100,
) -> list[dict]:
    """Fetch bioactivities for a ChEMBL target."""
    resp = await client.get(
        f"{CHEMBL_BASE}/activity.json",
        params={"target_chembl_id": target_chembl_id, "limit": limit},
    )
    resp.raise_for_status()
    return resp.json().get("activities", [])


async def get_molecules(
    client: httpx.AsyncClient, chembl_ids: list[str]
) -> list[dict]:
    """Batch-fetch molecule details by ChEMBL IDs."""
    if not chembl_ids:
        return []
    molecules: list[dict] = []
    for i in range(0, len(chembl_ids), 50):
        batch = chembl_ids[i : i + 50]
        id_str = ";".join(batch)
        resp = await client.get(f"{CHEMBL_BASE}/molecule/set/{id_str}.json")
        resp.raise_for_status()
        molecules.extend(resp.json().get("molecules", []))
    return molecules


async def assess_compounds(
    client: httpx.AsyncClient, target_chembl_id: str
) -> dict:
    """Assess compound landscape for a target.

    Returns dict with: num_compounds, max_phase, top_compounds (sorted by max_phase desc).
    """
    activities = await get_activities(client, target_chembl_id)
    mol_ids = list({
        a["molecule_chembl_id"]
        for a in activities
        if a.get("molecule_chembl_id")
    })
    molecules = await get_molecules(client, mol_ids)

    top_compounds = sorted(
        [
            {
                "molecule_chembl_id": m.get("molecule_chembl_id"),
                "pref_name": m.get("pref_name"),
                "max_phase": m.get("max_phase", 0) or 0,
            }
            for m in molecules
        ],
        key=lambda x: x["max_phase"],
        reverse=True,
    )

    return {
        "num_compounds": len(molecules),
        "max_phase": top_compounds[0]["max_phase"] if top_compounds else 0,
        "top_compounds": top_compounds[:10],
    }
