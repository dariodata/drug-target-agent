from src.models import (
    GeneAssociation,
    DruggabilityProfile,
    LiteratureEvidence,
    TargetReport,
    ReconReport,
)


def test_gene_association_creation():
    ga = GeneAssociation(
        gene_symbol="APOE",
        ensembl_id="ENSG00000130203",
        association_score=0.85,
        target_name="apolipoprotein E",
    )
    assert ga.gene_symbol == "APOE"
    assert ga.association_score == 0.85


def test_druggability_profile_defaults():
    dp = DruggabilityProfile(
        gene_symbol="APOE",
        uniprot_accession="P02649",
        protein_class="Lipid transport",
    )
    assert dp.has_3d_structure is False
    assert dp.num_known_compounds == 0
    assert dp.max_phase_drug == 0
    assert dp.druggability_verdict == ""


def test_literature_evidence_creation():
    le = LiteratureEvidence(
        gene_symbol="APOE",
        disease="Alzheimer disease",
        num_recent_papers=42,
        key_findings_summary="Strong genetic link established.",
        support_level="supporting",
        top_pmids=["12345", "67890", "11111"],
    )
    assert le.support_level == "supporting"
    assert len(le.top_pmids) == 3


def test_target_report_composite_score():
    tr = TargetReport(
        gene_symbol="APOE",
        ensembl_id="ENSG00000130203",
        target_name="apolipoprotein E",
        association_score=0.85,
        druggability=DruggabilityProfile(
            gene_symbol="APOE",
            uniprot_accession="P02649",
            protein_class="Lipid transport",
            has_3d_structure=True,
            num_known_compounds=15,
            max_phase_drug=2,
            druggability_verdict="Moderate",
        ),
        literature=LiteratureEvidence(
            gene_symbol="APOE",
            disease="Alzheimer disease",
            num_recent_papers=42,
            key_findings_summary="Strong link.",
            support_level="supporting",
            top_pmids=["12345"],
        ),
        reasoning="Top genetic association with moderate druggability.",
    )
    assert tr.gene_symbol == "APOE"
    assert tr.druggability.has_3d_structure is True


def test_recon_report_creation():
    report = ReconReport(
        disease="Alzheimer disease",
        disease_id="EFO_0000249",
        targets=[],
        recommendation="No targets found.",
    )
    assert report.disease == "Alzheimer disease"
    assert report.targets == []
