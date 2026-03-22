"""Reactome REST API wrapper for pathway information."""

import re

import httpx

REACTOME_URL = "https://reactome.org/ContentService"

_HTML_TAG_RE = re.compile(r"<[^>]+>")


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
        # Only keep actual Pathway groups
        if group.get("typeName") != "Pathway":
            continue
        for entry in group.get("entries", []):
            stable_id = entry.get("stId", "")
            name = entry.get("name", "")
            # Only human pathways (R-HSA prefix)
            if not stable_id.startswith("R-HSA"):
                continue
            # Strip HTML highlighting tags from names
            name = _HTML_TAG_RE.sub("", name)
            if stable_id and stable_id not in seen:
                seen.add(stable_id)
                pathways.append({
                    "reactome_id": stable_id,
                    "name": name,
                })

    return pathways
