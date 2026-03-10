"""UniProt REST API wrapper."""

import httpx

UNIPROT_URL = "https://rest.uniprot.org/uniprotkb/search"

FIELDS = ",".join([
    "accession",
    "gene_names",
    "protein_name",
    "organism_name",
    "cc_function",
    "cc_subcellular_location",
    "protein_families",
    "xref_pdb",
    "length",
    "reviewed",
])


async def fetch_protein_info(
    client: httpx.AsyncClient, gene_symbol: str
) -> dict | None:
    """Fetch protein info from UniProt for a human gene symbol.

    Returns dict with keys: accession, gene_symbol, function, subcellular_locations,
    pdb_ids, protein_families; or None if not found.
    """
    query = f"(gene:{gene_symbol}) AND (organism_id:9606) AND (reviewed:true)"
    resp = await client.get(
        UNIPROT_URL,
        params={"query": query, "format": "json", "fields": FIELDS, "size": 1},
    )
    resp.raise_for_status()
    results = resp.json().get("results", [])
    if not results:
        return None

    entry = results[0]
    accession = entry.get("primaryAccession", "")

    genes = [
        g["geneName"]["value"]
        for g in entry.get("genes", [])
        if "geneName" in g
    ]

    locations: list[str] = []
    functions: list[str] = []
    families: list[str] = []
    pdb_ids: list[str] = []

    for comment in entry.get("comments", []):
        ctype = comment.get("commentType", "")
        if ctype == "SUBCELLULAR LOCATION":
            for loc in comment.get("subcellularLocations", []):
                val = loc.get("location", {}).get("value")
                if val:
                    locations.append(val)
        elif ctype == "FUNCTION":
            for t in comment.get("texts", []):
                functions.append(t.get("value", ""))
        elif ctype == "SIMILARITY":
            for t in comment.get("texts", []):
                families.append(t.get("value", ""))

    for xref in entry.get("uniProtKBCrossReferences", []):
        if xref.get("database") == "PDB":
            pdb_ids.append(xref["id"])

    return {
        "accession": accession,
        "gene_symbol": genes[0] if genes else gene_symbol,
        "function": functions[0] if functions else "",
        "subcellular_locations": locations,
        "pdb_ids": pdb_ids,
        "protein_families": families,
    }
