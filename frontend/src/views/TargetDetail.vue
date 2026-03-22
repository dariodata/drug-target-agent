<template>
  <div class="page">
    <div v-if="loading" class="loading">Loading...</div>
    <template v-else-if="target">
      <div class="page-header">
        <h1>{{ target.gene_symbol }}</h1>
        <p>{{ target.target_name }}</p>
      </div>

      <div class="card-grid" style="margin-bottom: 24px;">
        <div class="card" style="padding: 14px;">
          <div class="label">Ensembl ID</div>
          <div style="margin-top: 4px; font-size: 13px;">{{ target.ensembl_id }}</div>
        </div>
        <div v-if="target.protein" class="card" style="padding: 14px;">
          <div class="label">UniProt</div>
          <div style="margin-top: 4px; font-size: 13px;">{{ target.protein.uniprot_accession }}</div>
        </div>
        <div v-if="target.protein" class="card" style="padding: 14px;">
          <div class="label">Protein Class</div>
          <div style="margin-top: 4px; font-size: 13px;">{{ target.protein.protein_class || '—' }}</div>
        </div>
        <div v-if="target.protein" class="card" style="padding: 14px;">
          <div class="label">3D Structure</div>
          <div style="margin-top: 4px; font-size: 13px;">{{ target.protein.has_3d_structure ? 'Yes' : 'No' }}</div>
        </div>
      </div>

      <!-- Diseases -->
      <div class="card" style="margin-bottom: 24px;">
        <h3 style="margin-bottom: 12px;">Associated Diseases</h3>
        <table>
          <thead><tr><th>Disease</th><th>Score</th></tr></thead>
          <tbody>
            <tr v-for="d in target.diseases" :key="d.efo_id" class="clickable" @click="$router.push('/disease/' + d.efo_id)">
              <td><router-link :to="'/disease/' + d.efo_id">{{ d.name }}</router-link></td>
              <td>
                <div class="score-bar"><div class="score-bar-fill" :style="{ width: (d.score * 100) + '%' }"></div></div>
                {{ d.score?.toFixed(3) }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Compounds -->
      <div v-if="target.compounds.length" class="card" style="margin-bottom: 24px;">
        <h3 style="margin-bottom: 12px;">Compounds ({{ target.compounds.length }})</h3>
        <table>
          <thead><tr><th>ChEMBL ID</th><th>Name</th><th>Max Phase</th></tr></thead>
          <tbody>
            <tr v-for="c in target.compounds" :key="c.chembl_id">
              <td><a :href="'https://www.ebi.ac.uk/chembl/compound_report_card/' + c.chembl_id" target="_blank">{{ c.chembl_id }}</a></td>
              <td>{{ c.pref_name || '—' }}</td>
              <td><span :class="'phase-pill phase-' + (c.max_phase ?? 0)">Phase {{ c.max_phase ?? 0 }}</span></td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Papers -->
      <div v-if="target.papers.length" class="card" style="margin-bottom: 24px;">
        <h3 style="margin-bottom: 12px;">Literature ({{ target.papers.length }})</h3>
        <table>
          <thead><tr><th>PMID</th><th>Title</th><th>Support</th></tr></thead>
          <tbody>
            <tr v-for="p in target.papers" :key="p.pmid">
              <td><a :href="'https://pubmed.ncbi.nlm.nih.gov/' + p.pmid" target="_blank">{{ p.pmid }}</a></td>
              <td>{{ p.title }}</td>
              <td>{{ p.support_level }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pathways -->
      <div v-if="target.pathways.length" class="card">
        <h3 style="margin-bottom: 12px;">Pathways ({{ target.pathways.length }})</h3>
        <table>
          <thead><tr><th>Reactome ID</th><th>Name</th></tr></thead>
          <tbody>
            <tr v-for="p in target.pathways" :key="p.reactome_id">
              <td><a :href="'https://reactome.org/content/detail/' + p.reactome_id" target="_blank">{{ p.reactome_id }}</a></td>
              <td>{{ p.name }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import api from '../api/client.js'

const props = defineProps({ symbol: { type: String, required: true } })
const loading = ref(true)
const target = ref(null)

async function loadTarget() {
  loading.value = true
  try {
    target.value = await api.getTarget(props.symbol)
  } catch (e) {
    console.error('Failed to load target', e)
  } finally {
    loading.value = false
  }
}

onMounted(loadTarget)
watch(() => props.symbol, loadTarget)
</script>
