"""MCP server exposing the drug-target reconnaissance toolkit.

Run with the MCP inspector for development:
    mcp dev src/mcp/server.py

Or register with Claude Desktop by adding to claude_desktop_config.json:
    {
      "mcpServers": {
        "drug-target": {
          "command": "uv",
          "args": ["--directory", "/path/to/drug-target-agent", "run", "python", "-m", "src.mcp.server"]
        }
      }
    }

Tools exposed:
    - search_targets(disease, top_n)              — Open Targets associations for a disease
    - get_protein_info(gene_symbol)               — UniProt entry summary for a human gene
    - get_alphafold_structure(uniprot_id)         — AlphaFold predicted structure + pLDDT
    - get_chembl_bioactivities(uniprot_accession) — ChEMBL compound landscape for a target
    - search_pubmed_tool(gene, disease, ...)      — PubMed papers linking gene to disease
    - get_reactome_pathways(gene_symbol)          — Reactome human pathways for a gene
"""
from __future__ import annotations

import httpx
from mcp.server.fastmcp import FastMCP

from src.tools.alphafold import fetch_alphafold_structure
from src.tools.chembl import assess_compounds, get_target_by_uniprot
from src.tools.open_targets import get_disease_targets, search_disease
from src.tools.pubmed import fetch_abstracts, search_papers
from src.tools.reactome import fetch_pathways
from src.tools.uniprot import fetch_protein_info

mcp = FastMCP("drug-target")

_TIMEOUT = 30.0


@mcp.tool()
async def search_targets(disease: str, top_n: int = 10) -> dict:
    """Search Open Targets for gene targets associated with a disease.

    Args:
        disease: Disease name (e.g. "Alzheimer disease").
        top_n: Number of top-ranked targets to return.

    Returns:
        Dict with the resolved disease name, EFO id, and a `targets` list of
        {gene_symbol, ensembl_id, target_name, association_score,
        datatype_scores}. Returns {"error": "disease_not_found", ...} if the
        disease name does not resolve to an EFO entry.
    """
    async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
        resolved = await search_disease(client, disease)
        if resolved is None:
            return {"error": "disease_not_found", "disease": disease}
        targets = await get_disease_targets(client, resolved["id"], top_n=top_n)
    return {
        "disease": resolved["name"],
        "disease_id": resolved["id"],
        "targets": targets,
    }


@mcp.tool()
async def get_protein_info(gene_symbol: str) -> dict:
    """Fetch UniProt entry summary for a human gene symbol.

    Args:
        gene_symbol: HGNC gene symbol (e.g. "APP").

    Returns:
        Dict with accession (UniProt id), gene_symbol, function,
        subcellular_locations, pdb_ids, protein_families. Returns
        {"error": "not_found", ...} if no reviewed human entry matches.
    """
    async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
        info = await fetch_protein_info(client, gene_symbol)
    if info is None:
        return {"error": "not_found", "gene_symbol": gene_symbol}
    return info


@mcp.tool()
async def get_alphafold_structure(uniprot_id: str) -> dict:
    """Fetch AlphaFold structure summary for a UniProt accession.

    Args:
        uniprot_id: UniProt accession (e.g. "P05067" for human APP).

    Returns:
        Dict with pdb_url, cif_url, plddt_mean, organism, description,
        created_date. Returns {"error": "no_prediction", ...} if no
        AlphaFold model exists for this accession.
    """
    result = await fetch_alphafold_structure(uniprot_id)
    if result is None:
        return {"error": "no_prediction", "uniprot_id": uniprot_id}
    return result.model_dump()


@mcp.tool()
async def get_chembl_bioactivities(uniprot_accession: str) -> dict:
    """Fetch the ChEMBL compound landscape for a target by UniProt accession.

    Args:
        uniprot_accession: UniProt accession (e.g. "P05067").

    Returns:
        Dict with target_chembl_id, pref_name, num_compounds, max_phase,
        and top_compounds (sorted by max_phase desc). Returns
        {"error": "no_chembl_target", ...} if the accession does not map
        to a ChEMBL target.
    """
    async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
        target = await get_target_by_uniprot(client, uniprot_accession)
        if target is None:
            return {"error": "no_chembl_target", "uniprot_accession": uniprot_accession}
        target_chembl_id = target.get("target_chembl_id", "")
        assessment = await assess_compounds(client, target_chembl_id)
    return {
        "target_chembl_id": target_chembl_id,
        "pref_name": target.get("pref_name"),
        **assessment,
    }


@mcp.tool()
async def search_pubmed_tool(
    gene: str, disease: str, max_results: int = 10
) -> dict:
    """Search PubMed for papers linking a gene to a disease.

    Args:
        gene: Gene symbol (e.g. "APP").
        disease: Disease term (e.g. "Alzheimer disease").
        max_results: Number of papers to fetch (default 10).

    Returns:
        Dict with total_count (total matches in PubMed) and papers, a list
        of {pmid, title, abstract, authors, journal, pub_date}.
    """
    async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
        pmids, total = await search_papers(client, gene, disease, max_results=max_results)
        papers = await fetch_abstracts(client, pmids)
    return {"total_count": total, "papers": papers}


@mcp.tool()
async def get_reactome_pathways(gene_symbol: str) -> dict:
    """Fetch human Reactome pathways for a gene symbol.

    Args:
        gene_symbol: HGNC gene symbol (e.g. "APP").

    Returns:
        Dict with gene_symbol and pathways, a list of {reactome_id, name}.
    """
    async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
        pathways = await fetch_pathways(client, gene_symbol)
    return {"gene_symbol": gene_symbol, "pathways": pathways}


if __name__ == "__main__":
    mcp.run()
