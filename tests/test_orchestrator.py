from unittest.mock import AsyncMock, patch
import pytest

from src.models import (
    GeneAssociation,
    DruggabilityProfile,
    LiteratureEvidence,
    TargetReport,
    ReconReport,
)
from src.orchestrator import run_recon, format_report_markdown


@pytest.mark.asyncio
async def test_run_recon():
    mock_genes = [
        GeneAssociation(
            gene_symbol="APOE",
            ensembl_id="ENSG00000130203",
            association_score=0.85,
            target_name="apolipoprotein E",
        ),
    ]
    mock_druggability = DruggabilityProfile(
        gene_symbol="APOE",
        uniprot_accession="P02649",
        protein_class="Lipid transport",
        has_3d_structure=True,
        num_known_compounds=5,
        max_phase_drug=2,
        druggability_verdict="Moderate",
    )
    mock_literature = LiteratureEvidence(
        gene_symbol="APOE",
        disease="Alzheimer disease",
        num_recent_papers=42,
        key_findings_summary="Strong genetic link.",
        support_level="supporting",
        top_pmids=["12345"],
    )

    with (
        patch("src.orchestrator.run_gene_hunter", new_callable=AsyncMock) as mock_gh,
        patch("src.orchestrator.run_druggability_assessor", new_callable=AsyncMock) as mock_da,
        patch("src.orchestrator.run_literature_validator", new_callable=AsyncMock) as mock_lv,
        patch("src.orchestrator.call_llm", new_callable=AsyncMock) as mock_llm,
    ):
        mock_gh.return_value = mock_genes
        mock_da.return_value = mock_druggability
        mock_lv.return_value = mock_literature
        mock_llm.return_value = "APOE is the top target due to strong genetic evidence and moderate druggability."

        report = await run_recon("Alzheimer disease")

    assert isinstance(report, ReconReport)
    assert report.disease == "Alzheimer disease"
    assert len(report.targets) == 1
    assert report.targets[0].gene_symbol == "APOE"
    assert report.recommendation != ""
    mock_gh.assert_called_once()


def test_report_structure():
    """Verify the full report has expected structure and content."""
    report = ReconReport(
        disease="Alzheimer disease",
        disease_id="EFO_0000249",
        targets=[
            TargetReport(
                gene_symbol="APOE",
                ensembl_id="ENSG00000130203",
                target_name="apolipoprotein E",
                association_score=0.85,
                druggability=DruggabilityProfile(
                    gene_symbol="APOE",
                    uniprot_accession="P02649",
                    protein_class="Lipid transport",
                    has_3d_structure=True,
                    num_known_compounds=5,
                    max_phase_drug=2,
                    druggability_verdict="Moderate druggability.",
                ),
                literature=LiteratureEvidence(
                    gene_symbol="APOE",
                    disease="Alzheimer disease",
                    num_recent_papers=42,
                    key_findings_summary="Strong genetic link.",
                    support_level="supporting",
                    top_pmids=["12345", "67890"],
                ),
                reasoning="Top target.",
            ),
        ],
        recommendation="APOE is the top target.",
    )

    md = format_report_markdown(report)
    assert "# Drug Target Reconnaissance: Alzheimer disease" in md
    assert "APOE" in md
    assert "Moderate druggability" in md
    assert "12345" in md

    # JSON round-trip
    json_data = report.model_dump()
    reconstructed = ReconReport(**json_data)
    assert reconstructed.disease == "Alzheimer disease"
    assert len(reconstructed.targets) == 1
