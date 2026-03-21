"""Reactome REST API wrapper for pathway information."""

import httpx

REACTOME_URL = "https://reactome.org/ContentService"


async def fetch_pathways(
    client: httpx.AsyncClient, gene_symbol: str
) -> list[dict]:
    """Fetch Reactome pathways for a human gene symbol.

    Returns list of dicts with keys: reactome_id, name.
    """
    resp = await client.get(
        f"{REACTOME_URL}/search/query",
        params={
            "query": gene_symbol,
            "species": "Homo sapiens",
            "types": "Pathway",
            "cluster": "true",
        },
    )
    resp.raise_for_status()
    data = resp.json()

    pathways: list[dict] = []
    seen: set[str] = set()
    for group in data.get("results", []):
        for entry in group.get("entries", []):
            stable_id = entry.get("stId", "")
            name = entry.get("name", "")
            if stable_id and stable_id not in seen:
                seen.add(stable_id)
                pathways.append({
                    "reactome_id": stable_id,
                    "name": name,
                })

    return pathways
