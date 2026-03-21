"""Pydantic models for structured agent inputs and outputs."""

from pydantic import BaseModel, Field


class GeneAssociation(BaseModel):
    """A gene target associated with a disease from Open Targets."""
    gene_symbol: str
    ensembl_id: str
    association_score: float
    target_name: str
    datatype_scores: dict[str, float] = Field(default_factory=dict)


class DruggabilityProfile(BaseModel):
    """Druggability assessment for a single gene target."""
    gene_symbol: str
    uniprot_accession: str
    protein_class: str
    subcellular_locations: list[str] = Field(default_factory=list)
    has_3d_structure: bool = False
    num_known_compounds: int = 0
    max_phase_drug: int = 0
    top_compounds: list[dict] = Field(default_factory=list)
    druggability_verdict: str = ""


class LiteratureEvidence(BaseModel):
    """Literature validation for a gene-disease pair."""
    gene_symbol: str
    disease: str
    num_recent_papers: int
    key_findings_summary: str
    support_level: str  # "supporting", "contradicting", "inconclusive"
    top_pmids: list[str] = Field(default_factory=list)


class Pathway(BaseModel):
    """A biological pathway from Reactome."""
    reactome_id: str
    name: str


class TargetReport(BaseModel):
    """Combined assessment of a single drug target candidate."""
    gene_symbol: str
    ensembl_id: str
    target_name: str
    association_score: float
    druggability: DruggabilityProfile
    literature: LiteratureEvidence
    pathways: list[Pathway] = Field(default_factory=list)
    reasoning: str


class ReconReport(BaseModel):
    """Final output: ranked drug target reconnaissance report."""
    disease: str
    disease_id: str
    targets: list[TargetReport]
    recommendation: str
