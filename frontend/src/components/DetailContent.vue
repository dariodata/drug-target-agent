<template>
  <div class="detail-content">
    <!-- Loading skeleton -->
    <div v-if="loading" class="panel-content">
      <div class="skeleton skeleton-line"></div>
      <div class="skeleton skeleton-line short"></div>
      <div class="skeleton skeleton-line"></div>
      <div class="skeleton skeleton-line short"></div>
    </div>

    <!-- Error state -->
    <div v-else-if="error" class="panel-error">
      <p>Failed to load details</p>
      <button class="retry-btn" @click="fetchData">Retry</button>
    </div>

    <template v-else>
      <!-- Tabs -->
      <div class="panel-tabs">
        <button
          v-for="t in availableTabs"
          :key="t.key"
          :class="['panel-tab', { active: activeTab === t.key }]"
          @click="activeTab = t.key"
        >
          {{ t.label }}
          <span v-if="t.count != null" class="tab-count">{{ t.count }}</span>
        </button>
      </div>

      <!-- Content -->
      <div class="panel-content tab-fade" :key="activeTab">
        <!-- INFO TAB (all types) -->
        <template v-if="activeTab === 'info'">
          <!-- Gene Info -->
          <template v-if="node.type === 'gene' && apiData">
            <div class="info-grid">
              <div class="info-item">
                <div class="info-label">Ensembl ID</div>
                <div class="info-value mono">{{ apiData.ensembl_id }}</div>
              </div>
              <div class="info-item" v-if="apiData.protein">
                <div class="info-label">UniProt</div>
                <div class="info-value mono">{{ apiData.protein.uniprot_accession }}</div>
              </div>
              <div class="info-item" v-if="apiData.protein">
                <div class="info-label">Protein Class</div>
                <div class="info-value">{{ apiData.protein.protein_class || '—' }}</div>
              </div>
              <div class="info-item" v-if="apiData.protein">
                <div class="info-label">3D Structure</div>
                <div class="info-value" :style="{ color: apiData.protein.has_3d_structure ? 'var(--protein)' : 'var(--text-dim)' }">
                  {{ apiData.protein.has_3d_structure ? '✓ Available' : 'Not available' }}
                </div>
              </div>
            </div>
            <div class="quick-stats">
              <div class="quick-stat">
                <div class="stat-num" style="color: var(--disease)">{{ apiData.diseases?.length || 0 }}</div>
                <div class="stat-label">Diseases</div>
              </div>
              <div class="quick-stat">
                <div class="stat-num" style="color: var(--compound)">{{ apiData.compounds?.length || 0 }}</div>
                <div class="stat-label">Compounds</div>
              </div>
              <div class="quick-stat">
                <div class="stat-num" style="color: var(--paper)">{{ apiData.papers?.length || 0 }}</div>
                <div class="stat-label">Papers</div>
              </div>
            </div>
            <div class="ext-links">
              <a :href="'https://ensembl.org/Homo_sapiens/Gene/Summary?g=' + apiData.ensembl_id" target="_blank" class="ext-link">Ensembl ↗</a>
              <a v-if="apiData.protein" :href="'https://www.uniprot.org/uniprot/' + apiData.protein.uniprot_accession" target="_blank" class="ext-link">UniProt ↗</a>
            </div>
          </template>

          <!-- Disease Info -->
          <template v-else-if="node.type === 'disease' && apiData">
            <div class="info-grid">
              <div class="info-item">
                <div class="info-label">EFO ID</div>
                <div class="info-value mono">{{ apiData.efo_id }}</div>
              </div>
              <div class="info-item">
                <div class="info-label">Name</div>
                <div class="info-value">{{ apiData.name }}</div>
              </div>
            </div>
            <div class="quick-stats">
              <div class="quick-stat">
                <div class="stat-num" style="color: var(--gene)">{{ apiData.targets?.length || 0 }}</div>
                <div class="stat-label">Targets</div>
              </div>
              <div class="quick-stat">
                <div class="stat-num" style="color: var(--paper)">{{ allPmids.length }}</div>
                <div class="stat-label">Papers</div>
              </div>
              <div class="quick-stat">
                <div class="stat-num" style="color: var(--pathway)">{{ allPathways.length }}</div>
                <div class="stat-label">Pathways</div>
              </div>
            </div>
          </template>

          <!-- Compound Info -->
          <template v-else-if="node.type === 'compound'">
            <div class="info-grid">
              <div class="info-item">
                <div class="info-label">ChEMBL ID</div>
                <div class="info-value mono">{{ node.id }}</div>
              </div>
              <div class="info-item" v-if="node.max_phase != null">
                <div class="info-label">Max Phase</div>
                <div class="info-value"><span :class="'phase-pill phase-' + node.max_phase">Phase {{ node.max_phase }}</span></div>
              </div>
            </div>
            <div class="ext-links">
              <a :href="'https://www.ebi.ac.uk/chembl/compound_report_card/' + node.id" target="_blank" class="ext-link">ChEMBL ↗</a>
            </div>
          </template>

          <!-- Protein Info -->
          <template v-else-if="node.type === 'protein'">
            <div class="info-grid">
              <div class="info-item">
                <div class="info-label">UniProt ID</div>
                <div class="info-value mono">{{ node.id }}</div>
              </div>
              <div class="info-item" v-if="node.protein_class">
                <div class="info-label">Protein Class</div>
                <div class="info-value">{{ node.protein_class }}</div>
              </div>
            </div>
            <div class="ext-links">
              <a :href="'https://www.uniprot.org/uniprot/' + node.id" target="_blank" class="ext-link">UniProt ↗</a>
            </div>
          </template>

          <!-- Paper Info -->
          <template v-else-if="node.type === 'paper'">
            <div class="info-grid">
              <div class="info-item">
                <div class="info-label">PMID</div>
                <div class="info-value mono">{{ node.id }}</div>
              </div>
              <div class="info-item" v-if="node.title">
                <div class="info-label">Title</div>
                <div class="info-value">{{ node.title }}</div>
              </div>
            </div>
            <div class="ext-links">
              <a :href="'https://pubmed.ncbi.nlm.nih.gov/' + node.id" target="_blank" class="ext-link">PubMed ↗</a>
            </div>
          </template>

          <!-- Pathway Info -->
          <template v-else-if="node.type === 'pathway'">
            <div class="info-grid">
              <div class="info-item">
                <div class="info-label">Reactome ID</div>
                <div class="info-value mono">{{ node.id }}</div>
              </div>
              <div class="info-item" v-if="node.label">
                <div class="info-label">Name</div>
                <div class="info-value">{{ node.label }}</div>
              </div>
            </div>
            <div class="ext-links">
              <a :href="'https://reactome.org/content/detail/' + node.id" target="_blank" class="ext-link">Reactome ↗</a>
            </div>
          </template>
        </template>

        <!-- DISEASES TAB (gene only) -->
        <template v-if="activeTab === 'diseases' && apiData">
          <table class="panel-table">
            <thead><tr><th>Disease</th><th>Score</th></tr></thead>
            <tbody>
              <tr v-for="d in apiData.diseases" :key="d.efo_id">
                <td>
                  <span class="navigate-link" @click="$emit('navigate', { id: d.efo_id, type: 'disease', label: d.name })">
                    {{ d.name }}
                  </span>
                </td>
                <td>
                  <div class="score-bar"><div class="score-bar-fill" :style="{ width: (d.score * 100) + '%' }"></div></div>
                  <span style="font-family: var(--font-mono); font-size: 11px;">{{ d.score?.toFixed(3) }}</span>
                </td>
              </tr>
            </tbody>
          </table>
        </template>

        <!-- TARGETS TAB (disease only) -->
        <template v-if="activeTab === 'targets' && apiData">
          <table class="panel-table">
            <thead><tr><th>Gene</th><th>Name</th><th>Score</th><th>Compounds</th></tr></thead>
            <tbody>
              <tr v-for="t in apiData.targets" :key="t.ensembl_id">
                <td>
                  <span class="navigate-link" @click="$emit('navigate', { id: t.ensembl_id, type: 'gene', label: t.gene_symbol, name: t.target_name })">
                    {{ t.gene_symbol }}
                  </span>
                </td>
                <td>{{ t.target_name }}</td>
                <td>
                  <div class="score-bar"><div class="score-bar-fill" :style="{ width: (t.association_score * 100) + '%' }"></div></div>
                  <span style="font-family: var(--font-mono); font-size: 11px;">{{ t.association_score?.toFixed(3) }}</span>
                </td>
                <td style="font-family: var(--font-mono); font-size: 11px;">{{ t.compounds.length }}</td>
              </tr>
            </tbody>
          </table>
        </template>

        <!-- COMPOUNDS TAB (gene only) -->
        <template v-if="activeTab === 'compounds' && apiData">
          <table class="panel-table">
            <thead><tr><th>ChEMBL ID</th><th>Name</th><th>Max Phase</th></tr></thead>
            <tbody>
              <tr v-for="c in apiData.compounds" :key="c.chembl_id">
                <td><a :href="'https://www.ebi.ac.uk/chembl/compound_report_card/' + c.chembl_id" target="_blank" style="font-family: var(--font-mono); font-size: 11px;">{{ c.chembl_id }}</a></td>
                <td>{{ c.pref_name || '—' }}</td>
                <td><span :class="'phase-pill phase-' + (c.max_phase ?? 0)">Phase {{ c.max_phase ?? 0 }}</span></td>
              </tr>
            </tbody>
          </table>
        </template>

        <!-- LITERATURE TAB (gene or disease) -->
        <template v-if="activeTab === 'literature'">
          <template v-if="node.type === 'gene' && apiData">
            <table class="panel-table">
              <thead><tr><th>PMID</th><th>Title</th><th>Support</th></tr></thead>
              <tbody>
                <tr v-for="p in apiData.papers" :key="p.pmid">
                  <td><a :href="'https://pubmed.ncbi.nlm.nih.gov/' + p.pmid" target="_blank" style="font-family: var(--font-mono); font-size: 11px;">{{ p.pmid }}</a></td>
                  <td>{{ p.title }}</td>
                  <td>{{ p.support_level }}</td>
                </tr>
              </tbody>
            </table>
          </template>
          <template v-else-if="node.type === 'disease' && apiData">
            <table class="panel-table">
              <thead><tr><th>PMID</th><th>Gene</th></tr></thead>
              <tbody>
                <tr v-for="p in allPmids" :key="p.pmid + p.gene">
                  <td><a :href="'https://pubmed.ncbi.nlm.nih.gov/' + p.pmid" target="_blank" style="font-family: var(--font-mono); font-size: 11px;">{{ p.pmid }}</a></td>
                  <td>
                    <span class="navigate-link" @click="$emit('navigate', { id: '', type: 'gene', label: p.gene })">
                      {{ p.gene }}
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
          </template>
        </template>

        <!-- PATHWAYS TAB (gene or disease) -->
        <template v-if="activeTab === 'pathways'">
          <template v-if="node.type === 'gene' && apiData">
            <table class="panel-table">
              <thead><tr><th>Reactome ID</th><th>Name</th></tr></thead>
              <tbody>
                <tr v-for="p in apiData.pathways" :key="p.reactome_id">
                  <td><a :href="'https://reactome.org/content/detail/' + p.reactome_id" target="_blank" style="font-family: var(--font-mono); font-size: 11px;">{{ p.reactome_id }}</a></td>
                  <td>{{ p.name }}</td>
                </tr>
              </tbody>
            </table>
          </template>
          <template v-else-if="node.type === 'disease' && apiData">
            <table class="panel-table">
              <thead><tr><th>Reactome ID</th><th>Name</th><th>Gene</th></tr></thead>
              <tbody>
                <tr v-for="p in allPathways" :key="p.reactome_id + p.gene">
                  <td><a :href="'https://reactome.org/content/detail/' + p.reactome_id" target="_blank" style="font-family: var(--font-mono); font-size: 11px;">{{ p.reactome_id }}</a></td>
                  <td>{{ p.name }}</td>
                  <td>
                    <span class="navigate-link" @click="$emit('navigate', { id: '', type: 'gene', label: p.gene })">
                      {{ p.gene }}
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
          </template>
        </template>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import api from '../api/client.js'

const props = defineProps({
  node: { type: Object, required: true },
})

const emit = defineEmits(['navigate'])

const loading = ref(false)
const error = ref(false)
const apiData = ref(null)
const activeTab = ref('info')

const tabDefs = {
  gene: [
    { key: 'info', label: 'Info' },
    { key: 'diseases', label: 'Diseases', countKey: 'diseases' },
    { key: 'compounds', label: 'Compounds', countKey: 'compounds' },
    { key: 'literature', label: 'Literature', countKey: 'papers' },
    { key: 'pathways', label: 'Pathways', countKey: 'pathways' },
  ],
  disease: [
    { key: 'info', label: 'Info' },
    { key: 'targets', label: 'Targets', countKey: 'targets' },
    { key: 'literature', label: 'Literature', countFn: 'pmids' },
    { key: 'pathways', label: 'Pathways', countFn: 'pathways' },
  ],
  compound: [{ key: 'info', label: 'Info' }],
  protein: [{ key: 'info', label: 'Info' }],
  paper: [{ key: 'info', label: 'Info' }],
  pathway: [{ key: 'info', label: 'Info' }],
}

const allPmids = computed(() => {
  if (!apiData.value?.targets) return []
  return apiData.value.targets.flatMap(t =>
    t.pmids.map(pmid => ({ pmid, gene: t.gene_symbol }))
  )
})

const allPathways = computed(() => {
  if (!apiData.value?.targets) return []
  return apiData.value.targets.flatMap(t =>
    t.pathways.map(p => ({ ...p, gene: t.gene_symbol }))
  )
})

const availableTabs = computed(() => {
  const defs = tabDefs[props.node.type] || [{ key: 'info', label: 'Info' }]
  return defs.map(d => {
    let count = null
    if (apiData.value && d.countKey) {
      count = apiData.value[d.countKey]?.length ?? 0
    } else if (d.countFn === 'pmids') {
      count = allPmids.value.length
    } else if (d.countFn === 'pathways') {
      count = allPathways.value.length
    }
    return { ...d, count }
  })
})

async function fetchData() {
  const type = props.node.type
  if (type !== 'gene' && type !== 'disease') {
    apiData.value = null
    loading.value = false
    return
  }

  loading.value = true
  error.value = false
  apiData.value = null

  try {
    if (type === 'gene') {
      apiData.value = await api.getTarget(props.node.label)
    } else if (type === 'disease') {
      apiData.value = await api.getDisease(props.node.id)
    }
  } catch (e) {
    console.error('Failed to load detail data', e)
    error.value = true
  } finally {
    loading.value = false
  }
}

watch(() => props.node, () => {
  activeTab.value = 'info'
  fetchData()
}, { immediate: true })
</script>
