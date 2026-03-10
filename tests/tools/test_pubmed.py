import json
from pathlib import Path
import httpx
import pytest
import respx

from src.tools.pubmed import search_papers, fetch_abstracts

FIXTURES = Path(__file__).parent.parent / "fixtures"
ESEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
EFETCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"


@respx.mock
@pytest.mark.asyncio
async def test_search_papers():
    fixture = json.loads((FIXTURES / "pubmed_esearch.json").read_text())
    respx.get(ESEARCH_URL).mock(return_value=httpx.Response(200, json=fixture))

    async with httpx.AsyncClient() as client:
        pmids, total = await search_papers(client, "APOE", "Alzheimer disease")

    assert total == 142
    assert len(pmids) == 5
    assert pmids[0] == "38001234"


@respx.mock
@pytest.mark.asyncio
async def test_fetch_abstracts():
    xml_text = (FIXTURES / "pubmed_efetch.xml").read_text()
    respx.get(EFETCH_URL).mock(return_value=httpx.Response(200, text=xml_text))

    async with httpx.AsyncClient() as client:
        articles = await fetch_abstracts(client, ["38001234", "37995678"])

    assert len(articles) == 2
    assert articles[0]["pmid"] == "38001234"
    assert "APOE" in articles[0]["title"]
    assert len(articles[0]["abstract"]) > 0
    assert articles[1]["pmid"] == "37995678"
