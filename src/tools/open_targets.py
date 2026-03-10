"""Open Targets Platform GraphQL API wrapper."""

import httpx

OPENTARGETS_URL = "https://api.platform.opentargets.org/api/v4/graphql"

SEARCH_QUERY = """
query SearchDisease($q: String!) {
  search(queryString: $q, entityNames: ["disease"], page: {index: 0, size: 5}) {
    hits {
      id
      name
      entity
    }
  }
}
"""

ASSOCIATIONS_QUERY = """
query DiseaseTargets($efoId: String!, $size: Int!) {
  disease(efoId: $efoId) {
    id
    name
    associatedTargets(page: {index: 0, size: $size}) {
      count
      rows {
        target {
          id
          approvedSymbol
          approvedName
          biotype
        }
        score
        datatypeScores {
          id
          score
        }
      }
    }
  }
}
"""


async def search_disease(
    client: httpx.AsyncClient, disease_name: str
) -> dict | None:
    """Resolve a disease name to an Open Targets EFO ID.

    Returns {"id": "EFO_...", "name": "..."} or None if not found.
    """
    resp = await client.post(
        OPENTARGETS_URL,
        json={"query": SEARCH_QUERY, "variables": {"q": disease_name}},
    )
    resp.raise_for_status()
    hits = resp.json()["data"]["search"]["hits"]
    for hit in hits:
        if hit["entity"] == "disease":
            return {"id": hit["id"], "name": hit["name"]}
    return None


async def get_disease_targets(
    client: httpx.AsyncClient, disease_efo_id: str, *, top_n: int = 10
) -> list[dict]:
    """Fetch top N gene targets associated with a disease, ranked by association score.

    Returns list of dicts with keys: gene_symbol, ensembl_id, target_name,
    association_score, datatype_scores.
    """
    resp = await client.post(
        OPENTARGETS_URL,
        json={
            "query": ASSOCIATIONS_QUERY,
            "variables": {"efoId": disease_efo_id, "size": top_n},
        },
    )
    resp.raise_for_status()
    disease_data = resp.json()["data"]["disease"]
    if disease_data is None:
        return []

    results = []
    for row in disease_data["associatedTargets"]["rows"]:
        results.append({
            "gene_symbol": row["target"]["approvedSymbol"],
            "ensembl_id": row["target"]["id"],
            "target_name": row["target"]["approvedName"],
            "association_score": row["score"],
            "datatype_scores": {
                ds["id"]: ds["score"] for ds in row["datatypeScores"]
            },
        })
    return results
