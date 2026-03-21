"""Tests for the Neo4j loader using a mocked driver."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from src.models import (
    DruggabilityProfile,
    LiteratureEvidence,
    Pathway,
    ReconReport,
    TargetReport,
)
from src.neo4j_loader import create_constraints, load_report


def _make_report() -> ReconReport:
    """Create a minimal ReconReport for testing."""
    return ReconReport(
        disease="Huntington disease",
        disease_id="EFO_0000337",
        targets=[
            TargetReport(
                gene_symbol="HTT",
                ensembl_id="ENSG00000197386",
                target_name="Huntingtin",
                association_score=0.73,
                druggability=DruggabilityProfile(
                    gene_symbol="HTT",
                    uniprot_accession="P42858",
                    protein_class="enzyme",
                    subcellular_locations=["Cytoplasm"],
                    has_3d_structure=True,
                    num_known_compounds=88,
                    max_phase_drug=4,
                    top_compounds=[
                        {"chembl_id": "CHEMBL1234", "pref_name": "DrugA", "max_phase": 4},
                    ],
                    druggability_verdict="Highly druggable",
                ),
                literature=LiteratureEvidence(
                    gene_symbol="HTT",
                    disease="Huntington disease",
                    num_recent_papers=532,
                    key_findings_summary="Strong evidence",
                    support_level="supporting",
                    top_pmids=["12345678", "87654321"],
                ),
                pathways=[
                    Pathway(reactome_id="R-HSA-6794362", name="Synaptic signaling"),
                ],
                reasoning="Top candidate",
            ),
        ],
        recommendation="HTT is the top target.",
    )


class MockSession:
    """Async context manager that tracks Cypher calls."""

    def __init__(self):
        self.run = AsyncMock()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        pass


def _mock_driver():
    """Create a mock Neo4j async driver with proper context manager support."""
    session = MockSession()
    driver = MagicMock()
    driver.session.return_value = session
    return driver, session


@pytest.mark.asyncio
async def test_create_constraints():
    driver, session = _mock_driver()
    await create_constraints(driver)
    # Should run 6 constraint queries
    assert session.run.call_count == 6
    calls = [str(c) for c in session.run.call_args_list]
    assert any("Disease" in c for c in calls)
    assert any("Gene" in c for c in calls)
    assert any("Pathway" in c for c in calls)


@pytest.mark.asyncio
async def test_load_report():
    driver, session = _mock_driver()
    report = _make_report()

    counts = await load_report(driver, report)

    assert counts["diseases"] == 1
    assert counts["genes"] == 1
    assert counts["proteins"] == 1
    assert counts["compounds"] == 1
    assert counts["papers"] == 2
    assert counts["pathways"] == 1
    assert counts["reports"] == 1

    # Verify key Cypher calls were made
    cypher_calls = [c.args[0] for c in session.run.call_args_list]
    assert any("Disease" in q and "MERGE" in q for q in cypher_calls)
    assert any("Gene" in q and "MERGE" in q for q in cypher_calls)
    assert any("Protein" in q and "MERGE" in q for q in cypher_calls)
    assert any("Compound" in q and "MERGE" in q for q in cypher_calls)
    assert any("Paper" in q and "MERGE" in q for q in cypher_calls)
    assert any("Pathway" in q and "MERGE" in q for q in cypher_calls)
    assert any("ASSOCIATED_WITH" in q for q in cypher_calls)
    assert any("ENCODES" in q for q in cypher_calls)
    assert any("HAS_COMPOUND" in q for q in cypher_calls)
    assert any("MENTIONED_IN" in q for q in cypher_calls)
    assert any("INVOLVED_IN" in q for q in cypher_calls)
    assert any("COVERS" in q for q in cypher_calls)


@pytest.mark.asyncio
async def test_load_report_no_compounds():
    """Report with no compounds should still load cleanly."""
    driver, session = _mock_driver()
    report = _make_report()
    report.targets[0].druggability.top_compounds = []

    counts = await load_report(driver, report)
    assert counts["compounds"] == 0


@pytest.mark.asyncio
async def test_load_report_no_pathways():
    """Report with no pathways should still load cleanly."""
    driver, session = _mock_driver()
    report = _make_report()
    report.targets[0].pathways = []

    counts = await load_report(driver, report)
    assert counts["pathways"] == 0
