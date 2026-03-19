# Drug Target Reconnaissance: Schizophrenia

**Disease ID:** ENSG00000149295
**Targets analyzed:** 5

---

## 1. DRD2 — dopamine receptor D2

| Metric | Value |
|--------|-------|
| Association Score | 0.734 |
| UniProt Accession | P14416 |
| Protein Class | Belongs to the G-protein coupled receptor 1 family |
| 3D Structure | Yes |
| Known Compounds | 57 |
| Max Drug Phase | 4 |
| PubMed Papers | 461 |
| Evidence | inconclusive |

**Druggability:** DRD2 is a highly druggable target, being a well-characterized GPCR located at the cell membrane with numerous known ligands, including compounds in Phase 4 clinical development, and multiple available 3D structures supporting structure-based drug design.

**Literature:** ```json
{
  "support_level": "supporting",
  "key_findings": "Large-scale genome-wide association studies (GWAS) have identified DRD2 as a significant locus associated with schizophrenia. Specific DRD2 polymorphisms are linked to increased risk for schizophrenia, including treatment-resistant forms, and are associated with altered brain function in intermediate phenotypes. Functional studies further highlight the role of DRD2 in neural circuits regulating social behavior, a core symptom of the disorder."
}
```

**PMIDs:** 25056061, 36980961, 37777856

---

## 2. SHANK3 — SH3 and multiple ankyrin repeat domains 3

| Metric | Value |
|--------|-------|
| Association Score | 0.702 |
| UniProt Accession | Q9BYB0 |
| Protein Class | Unknown |
| 3D Structure | Yes |
| Known Compounds | 0 |
| Max Drug Phase | 0 |
| PubMed Papers | 63 |
| Evidence | inconclusive |

**Druggability:** As a scaffold protein involved in protein-protein interactions, primarily localized intracellularly, and with no known ligands or compounds in clinical development, SHANK3 appears to be a challenging target for traditional small molecule drug discovery.

**Literature:** ```json
{
  "support_level": "supporting",
  "key_findings": "SHANK3 is strongly implicated in schizophrenia through various mechanisms. Its promoter is hypermethylated in peripheral blood cells of first-episode schizophrenia patients, correlating with negative symptoms and cortical surface area, and dysregulated in cortical interneurons. Additionally, schizophrenia-linked SHANK3 mutations (e.g., R1117X) in mouse models lead to profound synaptic defects in the prefrontal cortex, altered dendritic spine dynamics, adolescent sleep disturbances, and dopaminergic hyperactivity, supporting its critical role in the neuropathology of the disorder."
}
```

**PMIDs:** 37211699, 37532012, 37144901

---

## 3. RTN4R — reticulon 4 receptor

| Metric | Value |
|--------|-------|
| Association Score | 0.671 |
| UniProt Accession | Q9BZR6 |
| Protein Class | Belongs to the Nogo receptor family |
| 3D Structure | Yes |
| Known Compounds | 0 |
| Max Drug Phase | 0 |
| PubMed Papers | 14 |
| Evidence | inconclusive |

**Druggability:** RTN4R, as a cell membrane receptor with existing 3D structures, possesses good targetability for drug discovery. However, the complete absence of known bioactive compounds or clinical programs indicates its druggability, particularly for small molecules, remains unproven.

**Literature:** ```json
{
  "support_level": "inconclusive",
  "key_findings": "While some studies found no significant association between common RTN4R polymorphisms and schizophrenia in specific populations (Chinese, Korean), others identified rare coding variants in RTN4R associated with the disease. These rare variants were shown to functionally impair LGI1-NgR1 signaling and affect growth cone formation in vitro, suggesting RTN4R may modulate schizophrenia risk or clinical expression in a subset of patients, particularly through rare, impactful variants."
}
```

**PMIDs:** 18043741, 27468420, 28892071

---

## 4. DRD3 — dopamine receptor D3

| Metric | Value |
|--------|-------|
| Association Score | 0.660 |
| UniProt Accession | P35462 |
| Protein Class | Belongs to the G-protein coupled receptor 1 family |
| 3D Structure | Yes |
| Known Compounds | 99 |
| Max Drug Phase | 2 |
| PubMed Papers | 187 |
| Evidence | inconclusive |

**Druggability:** DRD3 is a highly druggable G-protein coupled receptor located on the cell membrane, a validated and favorable target class, with multiple existing 3D structures to facilitate drug design. The presence of numerous bioactive compounds, including some in Phase 2 clinical trials, further confirms its tractability and potential for drug development.

**Literature:** ```json
{
  "support_level": "supporting",
  "key_findings": "DRD3 polymorphisms, particularly Ser9Gly, are significantly associated with antipsychotic treatment response in schizophrenia, where the Ser allele and Ser/Ser genotype contribute to poor response in Caucasians. Evidence also links DRD3 polymorphisms to clozapine resistance in treatment-resistant schizophrenia. While some studies suggest a small, ethnically specific association with schizophrenia susceptibility (e.g., in Caucasians), others found no direct link."
}
```

**PMIDs:** 36980961, 35835396, 9674978

---

## 5. MTHFR — methylenetetrahydrofolate reductase

| Metric | Value |
|--------|-------|
| Association Score | 0.658 |
| UniProt Accession | P42898 |
| Protein Class | Belongs to the methylenetetrahydrofolate reductase family |
| 3D Structure | Yes |
| Known Compounds | 0 |
| Max Drug Phase | 0 |
| PubMed Papers | 153 |
| Evidence | inconclusive |

**Druggability:** MTHFR is an enzyme with available 3D structures, which are positive indicators for druggability. However, the complete absence of known bioactive compounds or clinical candidates suggests this target is underexplored or poses significant challenges for ligand discovery.

**Literature:** ```json
{
  "support_level": "supporting",
  "key_findings": "MTHFR polymorphisms, specifically C677T and A1298C, are associated with an increased risk of schizophrenia, particularly in Asian and African populations, as evidenced by meta-analyses. The MTHFR C677T polymorphism also appears to interact with environmental factors such as childhood adversity to heighten schizophrenia risk. Additionally, MTHFR variations have been linked to cognitive impairment and an increased risk of metabolic syndrome in individuals with schizophrenia."
}
```

**PMIDs:** 40282401, 24938371, 29188628

---

## Recommendation

**DRD2** and **DRD3** are the most promising drug targets for schizophrenia, given their high druggability as GPCRs with existing clinical-stage compounds, robust genetic association (DRD2) and strong links to antipsychotic treatment response and resistance (DRD3). Conversely, **SHANK3** presents compelling mechanistic evidence through mutations leading to synaptic defects and dopaminergic hyperactivity; however, its intracellular scaffold nature poses significant druggability challenges requiring innovative modalities. **MTHFR** also offers a relevant genetic association, particularly in specific populations and for broader symptoms like cognitive impairment, but its druggability requires further exploration. Therefore, immediate efforts should prioritize lead optimization and compound development for DRD2/DRD3, while initiating exploratory studies into non-traditional therapeutic approaches for SHANK3 and comprehensively assessing MTHFR's tractability for intervention.