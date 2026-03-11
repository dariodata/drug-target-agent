"""NCBI PubMed E-utilities API wrapper."""

import asyncio
import xml.etree.ElementTree as ET
import os
import httpx

ESEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
EFETCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"


def _base_params() -> dict:
    """Common params required by NCBI."""
    params: dict = {"email": os.environ.get("NCBI_EMAIL", "user@example.com")}
    api_key = os.environ.get("NCBI_API_KEY")
    if api_key:
        params["api_key"] = api_key
    return params


async def search_papers(
    client: httpx.AsyncClient,
    gene: str,
    disease: str,
    *,
    max_results: int = 10,
) -> tuple[list[str], int]:
    """Search PubMed for papers linking a gene to a disease.

    Returns (list_of_pmids, total_count).
    """
    term = f'"{gene}"[Title/Abstract] AND "{disease}"[Title/Abstract]'
    params = {
        **_base_params(),
        "db": "pubmed",
        "term": term,
        "retmax": max_results,
        "retmode": "json",
        "sort": "relevance",
    }
    for _attempt in range(3):
        resp = await client.get(ESEARCH_URL, params=params)
        if resp.status_code == 429:  # Too many requests
            await asyncio.sleep(2)
            continue
        resp.raise_for_status()
        break
    result = resp.json()["esearchresult"]
    pmids = result.get("idlist", [])
    total = int(result.get("count", 0))
    return pmids, total


def _parse_pubmed_xml(xml_text: str) -> list[dict]:
    """Parse PubmedArticleSet XML into a list of article dicts."""
    root = ET.fromstring(xml_text)
    articles = []

    for article_el in root.findall(".//PubmedArticle"):
        medline = article_el.find("MedlineCitation")
        if medline is None:
            continue

        pmid_el = medline.find("PMID")
        pmid = pmid_el.text if pmid_el is not None else ""

        art = medline.find("Article")
        if art is None:
            continue

        title_el = art.find("ArticleTitle")
        title = title_el.text or "" if title_el is not None else ""

        # Abstract (may have multiple structured parts)
        abstract_parts = []
        abstract_el = art.find("Abstract")
        if abstract_el is not None:
            for at in abstract_el.findall("AbstractText"):
                label = at.get("Label", "")
                text = "".join(at.itertext())
                if label:
                    abstract_parts.append(f"{label}: {text}")
                else:
                    abstract_parts.append(text)
        abstract = " ".join(abstract_parts)

        # Authors
        authors = []
        author_list = art.find("AuthorList")
        if author_list is not None:
            for author in author_list.findall("Author"):
                last = author.findtext("LastName", "")
                fore = author.findtext("ForeName", "")
                if last:
                    authors.append(f"{last} {fore}".strip())

        # Journal + date
        journal_el = art.find("Journal/Title")
        journal = journal_el.text if journal_el is not None else ""

        pub_date_el = art.find("Journal/JournalIssue/PubDate")
        if pub_date_el is not None:
            year = pub_date_el.findtext("Year", "")
            month = pub_date_el.findtext("Month", "")
            pub_date = f"{year} {month}".strip()
        else:
            pub_date = ""

        articles.append({
            "pmid": pmid,
            "title": title,
            "abstract": abstract,
            "authors": authors,
            "journal": journal,
            "pub_date": pub_date,
        })

    return articles


async def fetch_abstracts(
    client: httpx.AsyncClient, pmids: list[str]
) -> list[dict]:
    """Fetch abstracts for a list of PMIDs from PubMed.

    Returns list of dicts with: pmid, title, abstract, authors, journal, pub_date.
    """
    if not pmids:
        return []
    params = {
        **_base_params(),
        "db": "pubmed",
        "id": ",".join(pmids),
        "rettype": "abstract",
        "retmode": "xml",
    }
    for _attempt in range(3):
        resp = await client.get(EFETCH_URL, params=params)
        if resp.status_code == 429:
            await asyncio.sleep(2)
            continue
        resp.raise_for_status()
        break
    return _parse_pubmed_xml(resp.text)
