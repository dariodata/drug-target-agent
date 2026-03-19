# Drug Target Reconnaissance: Alzheimer disease

**Disease ID:** ENSG00000080815
**Targets analyzed:** 5

---

## 1. PSEN1 — presenilin 1

| Metric | Value |
|--------|-------|
| Association Score | 0.867 |
| UniProt Accession | P49768 |
| Protein Class | Belongs to the peptidase A22A family |
| 3D Structure | Yes |
| Known Compounds | 24 |
| Max Drug Phase | 0 |
| PubMed Papers | 223 |
| Evidence | inconclusive |

**Druggability:** As a peptidase (enzyme) with multiple 3D structures available, PSEN1 is intrinsically tractable for structure-based drug discovery. However, the complete absence of clinical-phase compounds among known binders suggests significant challenges, likely stemming from its critical role in the gamma-secretase complex and the potential for severe on-target or off-target toxicities.

**Literature:** ```json
{
  "support_level": "supporting",
  "key_findings": "PSEN1 mutations are a direct cause of autosomal dominant early-onset Alzheimer disease (AD-EOAD), including de novo mutations found in sporadic cases. These mutations are widely used in murine models (e.g., APP-PSEN1ΔE9, 5xFAD mice) to induce AD-like pathology and evaluate therapeutic strategies. Moreover, PSEN1 mutation carriers exhibit elevated plasma P-tau217 levels years before estimated symptom onset, highlighting PSEN1 as a significant genetic risk factor linked to AD pathogenesis and microglial dysfunction."
}
```

**PMIDs:** 30898012, 32722745, 33622188

---

## 2. APP — amyloid beta precursor protein

| Metric | Value |
|--------|-------|
| Association Score | 0.854 |
| UniProt Accession | P05067 |
| Protein Class | Belongs to the APP family |
| 3D Structure | Yes |
| Known Compounds | 55 |
| Max Drug Phase | 3 |
| PubMed Papers | 1451 |
| Evidence | inconclusive |

**Druggability:** APP, as a cell surface receptor with numerous 3D structures and membrane localization, is highly druggable, supported by existing bioactive compounds and historical drug discovery efforts, some of which have reached clinical phases.

**Literature:** ```json
{
  "support_level": "supporting",
  "key_findings": "Mutations in the APP gene are a confirmed cause of early-onset Alzheimer disease (AD-EOAD), with genetic screening studies identifying APP duplications in both familial and sporadic cases. Furthermore, post-translational modifications of APP, such as lactylation, play a crucial role in AD pathogenesis by influencing amyloid-beta (Aβ) generation, protein trafficking, and degradation, suggesting novel therapeutic targets. Studies utilizing APP-based animal models also demonstrate that interventions impacting Aβ pathology can ameliorate disease markers, reinforcing APP's central role in the disease."
}
```

**PMIDs:** 39744941, 30266932, 38504517

---

## 3. PSEN2 — presenilin 2

| Metric | Value |
|--------|-------|
| Association Score | 0.817 |
| UniProt Accession | P49810 |
| Protein Class | Belongs to the peptidase A22A family |
| 3D Structure | Yes |
| Known Compounds | 9 |
| Max Drug Phase | 0 |
| PubMed Papers | 102 |
| Evidence | inconclusive |

**Druggability:** PSEN2, a membrane-bound enzyme with available 3D structures, presents good druggability potential for structure-based design. While early-stage compounds exist, the lack of clinical progress suggests challenges in developing selective modulators without off-target effects, possibly related to its critical roles in the gamma-secretase complex and calcium homeostasis.

**Literature:** ```json
{
  "support_level": "supporting",
  "key_findings": "Mutations in PSEN2 are consistently identified as a cause of autosomal dominant early-onset Alzheimer disease (AD-EOAD). Genetic screening studies report pathogenic PSEN2 variants in a subset of familial and sporadic EOAD cases, alongside mutations in APP and PSEN1, confirming its role in AD pathogenesis."
}
```

**PMIDs:** 28350801, 20301340, 35678406

---

## 4. APOE — apolipoprotein E

| Metric | Value |
|--------|-------|
| Association Score | 0.782 |
| UniProt Accession | P02649 |
| Protein Class | Belongs to the apolipoprotein A1/A4/E family |
| 3D Structure | Yes |
| Known Compounds | 0 |
| Max Drug Phase | 0 |
| PubMed Papers | 1588 |
| Evidence | inconclusive |

**Druggability:** While its extracellular location and numerous 3D structures are favorable for drug discovery, the absence of known bioactive compounds or clinical progress indicates APOE currently poses a significant challenge for conventional small-molecule drug development.

**Literature:** ```json
{
  "support_level": "supporting",
  "key_findings": "Apolipoprotein E (APOE) is consistently identified as the strongest genetic risk factor for late-onset Alzheimer disease (AD), with the ε4 allele increasing risk and the ε2 allele conferring protection relative to the common ε3 allele. APOE influences AD pathogenesis through multiple mechanisms, including driving amyloid and tau pathology, modulating neuroinflammation, and affecting lipid transport, synaptic function, and cerebrovascular health. Its multifaceted roles make APOE a significant target for precision medicine and therapeutic strategies in AD."
}
```

**PMIDs:** 31367008, 23296339, 38906999

---

## 5. GRIN1 — glutamate ionotropic receptor NMDA type subunit 1

| Metric | Value |
|--------|-------|
| Association Score | 0.684 |
| UniProt Accession | Q05586 |
| Protein Class | Belongs to the glutamate-gated ion channel (TC 1.A.10.1) family. NR1/GRIN1 subfamily |
| 3D Structure | Yes |
| Known Compounds | 63 |
| Max Drug Phase | 0 |
| PubMed Papers | 1 |
| Evidence | inconclusive |

**Druggability:** GRIN1 is a highly druggable target, being a well-characterized membrane-bound ligand-gated ion channel with numerous 3D structures suitable for structure-based drug design. While over 60 compounds are known, the absence of clinical progress beyond phase 0 indicates challenges in drug development, despite the inherent tractability of the target class.

**Literature:** ```json
{
  "support_level": "supporting",
  "key_findings": "Carriers of the rs11146020-G allele in GRIN1 are associated with an earlier age at onset of Alzheimer's disease dementia, particularly in APOE-ε4 non-carriers. This GRIN1 variant also influences behavioral symptoms in different dementia stages, leading to a complex impact on the disease course, including less aberrant motor behavior and apathy, but more disinhibition, often modulated by APOE-ε4 status."
}
```

**PMIDs:** 40441773

---

## Recommendation

**Recommendation:**

APP is the most promising immediate drug target due to its direct causal role in early-onset AD, high intrinsic druggability, and historical progress with compounds reaching clinical Phase 3. While PSEN1 and PSEN2 also represent direct genetic causes of AD, their clinical translation is challenging, as evidenced by the complete absence of clinical-phase compounds and the historical toxicity associated with gamma-secretase modulation. APOE is a critical, high-impact target for late-onset AD as the strongest genetic risk factor, but its current undruggability (zero known compounds) necessitates long-term, innovative discovery efforts beyond conventional small molecules. Therefore, we recommend prioritizing APP, focusing on highly specific Aβ modulatory strategies to overcome past clinical failures, while exploring novel, selective approaches for PSEN1/PSEN2 and initiating early-stage target validation for APOE with an emphasis on new modalities.