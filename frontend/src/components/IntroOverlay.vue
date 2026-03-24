<template>
  <Teleport to="body">
    <Transition name="intro-fade">
      <div v-if="visible" class="intro-dimmer" @click.self="close">
        <Transition name="intro-card" appear>
          <div class="intro-overlay">
            <button class="intro-close" @click="close">&times;</button>

            <div class="intro-scroll">
              <!-- Header -->
              <div class="intro-header">
                <h1>Drug Target Reconnaissance Agent</h1>
                <p class="intro-tagline">
                  A multi-agent system that takes a disease name and autonomously
                  finds potential drug targets by querying public bioinformatics
                  databases. It returns a ranked list of targets, each annotated
                  with protein structure data, known compounds, clinical trial
                  progress, and recent literature.
                </p>
              </div>

              <!-- The Problem -->
              <section class="intro-section">
                <div class="intro-label blue">The Problem</div>
                <p class="intro-text">
                  Early-stage drug target identification is a cross-referencing
                  exercise. Open Targets tells you which genes are associated with
                  a disease. UniProt tells you what the protein looks like. ChEMBL
                  tells you if compounds exist that bind it, and how far they've
                  progressed in trials. PubMed tells you what the literature says.
                  A scientist doing this manually queries each database, copies
                  results into a spreadsheet, and writes a recommendation. This
                  tool automates that entire workflow.
                </p>
              </section>

              <!-- How It Works -->
              <section class="intro-section">
                <div class="intro-label blue">How It Works</div>
                <div class="arch-flow">
                  <div class="arch-row">
                    <div class="arch-node orch">
                      Orchestrator
                      <span class="arch-sub">coordinates</span>
                    </div>
                    <span class="arch-arrow">&rarr;</span>
                    <div class="arch-node agent">
                      Gene Hunter
                      <span class="arch-sub">Open Targets</span>
                    </div>
                    <span class="arch-arrow">&rarr;</span>
                    <div class="arch-parallel-group">
                      <div class="arch-node agent">
                        Druggability
                        <span class="arch-sub">UniProt + ChEMBL</span>
                      </div>
                      <div class="arch-node agent">
                        Literature
                        <span class="arch-sub">PubMed</span>
                      </div>
                      <div class="arch-node api">
                        Reactome
                        <span class="arch-sub">Pathways</span>
                      </div>
                    </div>
                    <span class="arch-arrow">&rarr;</span>
                    <div class="arch-node llm">
                      LLM Synthesis
                      <span class="arch-sub">Ranked Report</span>
                    </div>
                  </div>
                  <div class="arch-note">
                    Three tasks run in parallel per gene via asyncio.gather()
                  </div>
                </div>
                <p class="intro-text">
                  The Gene Hunter queries Open Targets for disease-gene
                  associations. Then for each gene, three tasks run in parallel:
                  the Druggability Assessor checks protein annotations and existing
                  compounds, the Literature Validator searches PubMed abstracts,
                  and Reactome fetches biological pathways. Each agent uses an LLM
                  to interpret raw data into assessments. The orchestrator
                  synthesizes everything into a ranked report.
                </p>
              </section>

              <!-- What It Found -->
              <section class="intro-section">
                <div class="intro-label warm">What It Found</div>
                <p class="intro-text">
                  Results matched real-world pharmaceutical consensus across three
                  diseases, without any hardcoded domain knowledge:
                </p>
                <div class="findings-grid">
                  <div class="finding-card">
                    <div class="finding-disease">Alzheimer's</div>
                    <div class="finding-target">#1 APP</div>
                    <div class="finding-compounds">
                      55 compounds &middot; Phase 3
                    </div>
                    <div class="finding-detail">
                      Flagged APOE as strongest genetic risk factor but
                      undruggable: zero compounds, zero clinical progress
                    </div>
                  </div>
                  <div class="finding-card">
                    <div class="finding-disease">Parkinson's</div>
                    <div class="finding-target">#1 LRRK2</div>
                    <div class="finding-compounds">
                      54 compounds &middot; Phase 4
                    </div>
                    <div class="finding-detail">
                      Noted SNCA as intrinsically disordered, challenging for
                      conventional small molecule design
                    </div>
                  </div>
                  <div class="finding-card">
                    <div class="finding-disease">Schizophrenia</div>
                    <div class="finding-target">#1 DRD2</div>
                    <div class="finding-compounds">
                      57 compounds &middot; Phase 4
                    </div>
                    <div class="finding-detail">
                      Every antipsychotic on the market targets the dopamine D2
                      receptor
                    </div>
                  </div>
                </div>
              </section>

              <!-- Built With -->
              <section class="intro-section">
                <div class="intro-label teal">Built With</div>
                <div class="tech-grid">
                  <div class="tech-item">
                    <div class="tech-icon python">Py</div>
                    <div>
                      <div class="tech-name">Python</div>
                      <div class="tech-role">Async pipeline</div>
                    </div>
                  </div>
                  <div class="tech-item">
                    <div class="tech-icon gemini">G</div>
                    <div>
                      <div class="tech-name">Gemini 2.5</div>
                      <div class="tech-role">Agent reasoning</div>
                    </div>
                  </div>
                  <div class="tech-item">
                    <div class="tech-icon neo4j">N4j</div>
                    <div>
                      <div class="tech-name">Neo4j</div>
                      <div class="tech-role">Knowledge graph</div>
                    </div>
                  </div>
                  <div class="tech-item">
                    <div class="tech-icon vue">V</div>
                    <div>
                      <div class="tech-name">Vue.js</div>
                      <div class="tech-role">Frontend</div>
                    </div>
                  </div>
                  <div class="tech-item">
                    <div class="tech-icon cyto">Cy</div>
                    <div>
                      <div class="tech-name">Cytoscape.js</div>
                      <div class="tech-role">Graph visualization</div>
                    </div>
                  </div>
                </div>
              </section>

              <!-- Data Sources -->
              <section class="intro-section">
                <div class="intro-label teal">Data Sources</div>
                <p class="intro-text">
                  All five APIs are free. Open Targets, UniProt, ChEMBL, and
                  Reactome need no authentication. PubMed just needs an email
                  address.
                </p>
                <div class="sources-row">
                  <span class="source-badge">Open Targets <span class="source-free">free</span></span>
                  <span class="source-badge">UniProt <span class="source-free">free</span></span>
                  <span class="source-badge">ChEMBL <span class="source-free">free</span></span>
                  <span class="source-badge">Reactome <span class="source-free">free</span></span>
                  <span class="source-badge">PubMed <span class="source-free">free</span></span>
                </div>
              </section>

              <!-- Limitations -->
              <section class="intro-section">
                <div class="intro-label purple">Limitations</div>
                <ul class="limitations-list">
                  <li>
                    Single association source: only Open Targets for gene-disease
                    links (could add GWAS Catalog, DisGeNET)
                  </li>
                  <li>
                    Abstracts only: PubMed search uses abstracts, not full text,
                    so the literature agent misses nuance
                  </li>
                  <li>
                    Limited clinical trial data: ChEMBL's "max phase" field only;
                    a ClinicalTrials.gov agent would add trial design details
                  </li>
                </ul>
              </section>

              <!-- Learn More -->
              <section class="intro-section">
                <div class="intro-label gray">Learn More</div>
                <div class="links-row">
                  <a
                    class="link-card"
                    href="https://github.com/dariodata/drug-target-agent/blob/main/blog-post.md"
                    target="_blank"
                    rel="noopener"
                  >
                    <div class="link-title">Read the Blog Post &rarr;</div>
                    <div class="link-desc">
                      Deep dive into the architecture, full disease findings with
                      PubMed citations, and what's next
                    </div>
                  </a>
                  <a
                    class="link-card"
                    href="https://github.com/dariodata/drug-target-agent"
                    target="_blank"
                    rel="noopener"
                  >
                    <div class="link-title">View on GitHub &rarr;</div>
                    <div class="link-desc">
                      Source code, setup instructions, pre-generated reports, and
                      the full test suite
                    </div>
                  </a>
                </div>
              </section>
            </div>

            <!-- Sticky CTA -->
            <div class="intro-cta">
              <button class="cta-btn" @click="close">
                Explore the Knowledge Graph
              </button>
              <div class="cta-hint">
                Click any node to see target details, compounds, and literature
              </div>
            </div>
          </div>
        </Transition>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { onMounted, onUnmounted } from 'vue'

const props = defineProps({
  visible: { type: Boolean, default: true }
})

const emit = defineEmits(['close'])

function close() {
  emit('close')
}

function onKeydown(e) {
  if (e.key === 'Escape' && props.visible) {
    close()
  }
}

onMounted(() => {
  document.addEventListener('keydown', onKeydown)
})

onUnmounted(() => {
  document.removeEventListener('keydown', onKeydown)
})
</script>

<style scoped>
/* Dimmer */
.intro-dimmer {
  position: fixed;
  inset: 0;
  z-index: 30;
  background: rgba(0, 0, 0, 0.55);
  backdrop-filter: blur(2px);
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Overlay card */
.intro-overlay {
  position: relative;
  width: 580px;
  max-width: 90vw;
  max-height: 82vh;
  background: rgba(26, 29, 36, 0.96);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid var(--border);
  border-radius: 14px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  box-shadow: 0 24px 80px rgba(0, 0, 0, 0.5);
}

/* Close button */
.intro-close {
  position: absolute;
  top: 14px;
  right: 14px;
  z-index: 2;
  width: 28px;
  height: 28px;
  border-radius: 6px;
  border: 1px solid var(--border);
  background: rgba(37, 40, 50, 0.8);
  color: var(--text-dim);
  font-size: 18px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: border-color 0.15s, color 0.15s;
  line-height: 1;
}
.intro-close:hover {
  border-color: var(--accent);
  color: var(--text);
}

/* Scrollable content */
.intro-scroll {
  overflow-y: auto;
  padding: 28px 28px 20px;
  scrollbar-width: thin;
  scrollbar-color: var(--border) transparent;
}
.intro-scroll::-webkit-scrollbar {
  width: 6px;
}
.intro-scroll::-webkit-scrollbar-track {
  background: transparent;
}
.intro-scroll::-webkit-scrollbar-thumb {
  background: var(--border);
  border-radius: 3px;
}

/* Header */
.intro-header {
  text-align: center;
  margin-bottom: 22px;
}
.intro-header h1 {
  font-size: 22px;
  font-weight: 700;
  letter-spacing: -0.5px;
  margin-bottom: 10px;
}
.intro-tagline {
  color: var(--text-dim);
  font-size: 13px;
  line-height: 1.65;
  max-width: 460px;
  margin: 0 auto;
}

/* Sections */
.intro-section {
  margin-bottom: 22px;
}
.intro-label {
  font-size: 10px;
  text-transform: uppercase;
  letter-spacing: 1px;
  font-weight: 600;
  margin-bottom: 8px;
  padding-bottom: 4px;
  border-bottom: 1px solid var(--border);
}
.intro-label.blue { color: var(--accent); }
.intro-label.warm { color: var(--accent-warm); }
.intro-label.teal { color: var(--pathway); }
.intro-label.purple { color: var(--paper); }
.intro-label.gray { color: var(--text-dim); }

.intro-text {
  color: var(--text-dim);
  font-size: 12px;
  line-height: 1.7;
}

/* Architecture flow */
.arch-flow {
  background: var(--bg-card);
  border-radius: 8px;
  padding: 14px;
  margin: 10px 0;
}
.arch-row {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  flex-wrap: wrap;
}
.arch-node {
  background: var(--bg-hover);
  border: 1px solid;
  padding: 6px 10px;
  border-radius: 6px;
  font-size: 10px;
  font-weight: 500;
  text-align: center;
  line-height: 1.3;
}
.arch-node.orch { border-color: #7b68ee; color: #7b68ee; }
.arch-node.agent { border-color: #2d9c6f; color: #2d9c6f; }
.arch-node.api { border-color: var(--accent); color: var(--accent); }
.arch-node.llm { border-color: #d94a6e; color: #d94a6e; }
.arch-sub {
  display: block;
  font-size: 8px;
  color: var(--text-faint);
  margin-top: 2px;
}
.arch-arrow {
  color: var(--text-faint);
  font-size: 14px;
  flex-shrink: 0;
}
.arch-parallel-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.arch-note {
  text-align: center;
  font-size: 9px;
  color: #7b68ee;
  font-style: italic;
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px dashed var(--border);
}

/* Findings */
.findings-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
  margin-top: 10px;
}
.finding-card {
  background: var(--bg-card);
  border-radius: 8px;
  padding: 10px;
  border-left: 3px solid var(--disease);
}
.finding-disease {
  font-size: 11px;
  font-weight: 600;
  color: var(--text);
  margin-bottom: 3px;
}
.finding-target {
  font-size: 10px;
  color: var(--accent);
  font-weight: 600;
}
.finding-compounds {
  font-size: 9px;
  color: var(--text-dim);
  margin-top: 2px;
}
.finding-detail {
  font-size: 9px;
  color: var(--text-faint);
  margin-top: 4px;
  line-height: 1.4;
}

/* Tech stack */
.tech-grid {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-top: 8px;
}
.tech-item {
  background: var(--bg-card);
  border-radius: 6px;
  padding: 7px 11px;
  display: flex;
  align-items: center;
  gap: 8px;
  border: 1px solid var(--border);
}
.tech-icon {
  width: 22px;
  height: 22px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 9px;
  font-weight: 700;
  flex-shrink: 0;
}
.tech-icon.python { background: #306998; color: #FFD43B; }
.tech-icon.gemini { background: #4285F4; color: white; }
.tech-icon.neo4j { background: #018BFF; color: white; }
.tech-icon.vue { background: #42b883; color: white; }
.tech-icon.cyto { background: #e74c3c; color: white; }
.tech-name {
  font-size: 11px;
  color: var(--text);
  font-weight: 500;
}
.tech-role {
  font-size: 9px;
  color: var(--text-faint);
}

/* Data sources */
.sources-row {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  margin-top: 8px;
}
.source-badge {
  background: var(--bg-hover);
  border: 1px solid var(--border);
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 10px;
  color: var(--text-dim);
}
.source-free {
  font-size: 8px;
  color: #2d9c6f;
  margin-left: 3px;
}

/* Limitations */
.limitations-list {
  list-style: none;
  padding: 0;
  margin-top: 6px;
}
.limitations-list li {
  font-size: 11px;
  color: var(--text-dim);
  padding: 4px 0 4px 16px;
  position: relative;
  line-height: 1.5;
}
.limitations-list li::before {
  content: '';
  position: absolute;
  left: 0;
  top: 10px;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--text-faint);
}

/* Links */
.links-row {
  display: flex;
  gap: 10px;
  margin-top: 10px;
}
.link-card {
  flex: 1;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 10px 14px;
  text-decoration: none;
  cursor: pointer;
  transition: border-color 0.15s;
  display: block;
}
.link-card:hover {
  border-color: var(--accent);
}
.link-title {
  font-size: 11px;
  color: var(--accent);
  font-weight: 600;
  margin-bottom: 2px;
}
.link-desc {
  font-size: 9px;
  color: var(--text-faint);
  line-height: 1.4;
}

/* Sticky CTA */
.intro-cta {
  padding: 16px 28px 20px;
  border-top: 1px solid var(--border);
  text-align: center;
  background: rgba(26, 29, 36, 0.98);
  flex-shrink: 0;
}
.cta-btn {
  display: inline-block;
  background: var(--accent);
  color: var(--bg);
  font-size: 13px;
  font-weight: 600;
  padding: 10px 32px;
  border-radius: 8px;
  border: none;
  cursor: pointer;
  transition: background 0.15s;
}
.cta-btn:hover {
  background: var(--accent-hover);
}
.cta-hint {
  font-size: 10px;
  color: var(--text-faint);
  margin-top: 6px;
}

/* Transitions */
.intro-fade-enter-active,
.intro-fade-leave-active {
  transition: opacity 0.2s ease;
}
.intro-fade-enter-from,
.intro-fade-leave-to {
  opacity: 0;
}

.intro-card-enter-active {
  transition: opacity 0.25s ease, transform 0.25s cubic-bezier(0.16, 1, 0.3, 1);
}
.intro-card-leave-active {
  transition: opacity 0.15s ease, transform 0.15s ease;
}
.intro-card-enter-from {
  opacity: 0;
  transform: scale(0.95);
}
.intro-card-leave-to {
  opacity: 0;
  transform: scale(0.97);
}

/* Responsive */
@media (max-width: 600px) {
  .findings-grid {
    grid-template-columns: 1fr;
  }
  .tech-grid {
    flex-direction: column;
  }
  .links-row {
    flex-direction: column;
  }
  .arch-row {
    flex-direction: column;
    gap: 8px;
  }
  .arch-arrow {
    transform: rotate(90deg);
  }
}
</style>
