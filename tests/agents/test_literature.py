import json
from pathlib import Path
from unittest.mock import AsyncMock, patch
import pytest

from src.agents.literature import run_literature_validator
from src.models import LiteratureEvidence

FIXTURES = Path(__file__).parent.parent / "fixtures"


@pytest.mark.asyncio
async def test_run_literature_validator():
    esearch_fixture = json.loads((FIXTURES / "pubmed_esearch.json").read_text())
    efetch_xml = (FIXTURES / "pubmed_efetch.xml").read_text()

    mock_client = AsyncMock()

    async def mock_get(url, **kwargs):
        resp = AsyncMock()
        resp.raise_for_status = lambda: None
        if "esearch" in url:
            resp.json = lambda: esearch_fixture
        elif "efetch" in url:
            resp.text = efetch_xml
        return resp

    mock_client.get = mock_get

    with patch("src.agents.literature.call_llm", new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value = json.dumps({
            "support_level": "supporting",
            "key_findings": "Strong genetic evidence links APOE to Alzheimer disease risk."
        })
        evidence = await run_literature_validator(
            mock_client, "APOE", "Alzheimer disease"
        )

    assert isinstance(evidence, LiteratureEvidence)
    assert evidence.gene_symbol == "APOE"
    assert evidence.num_recent_papers == 142
    assert evidence.support_level == "supporting"
    assert len(evidence.top_pmids) > 0
