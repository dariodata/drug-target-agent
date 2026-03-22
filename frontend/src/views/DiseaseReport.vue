<template>
  <div class="page">
    <div v-if="loading" class="loading">Loading...</div>
    <template v-else-if="disease">
      <div class="page-header">
        <h1>{{ disease.name }}</h1>
        <p>{{ disease.efo_id }}</p>
      </div>

      <div class="tabs">
        <button :class="['tab', { active: tab === 'targets' }]" @click="tab = 'targets'">Targets ({{ disease.targets.length }})</button>
        <button :class="['tab', { active: tab === 'literature' }]" @click="tab = 'literature'">Literature ({{ allPmids.length }})</button>
        <button :class="['tab', { active: tab === 'pathways' }]" @click="tab = 'pathways'">Pathways ({{ allPathways.length }})</button>
      </div>

      <!-- Targets tab -->
      <div v-if="tab === 'targets'" class="card">
        <table>
          <thead>
            <tr>
              <th>Gene</th>
              <th>Name</th>
              <th>Score</th>
              <th>Protein Class</th>
              <th>Compounds</th>
              <th>3D</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="t in disease.targets" :key="t.ensembl_id" class="clickable" @click="$router.push('/target/' + t.gene_symbol)">
              <td><router-link :to="'/target/' + t.gene_symbol">{{ t.gene_symbol }}</router-link></td>
              <td>{{ t.target_name }}</td>
              <td>
                <div class="score-bar"><div class="score-bar-fill" :style="{ width: (t.association_score * 100) + '%' }"></div></div>
                {{ t.association_score?.toFixed(3) }}
              </td>
              <td>{{ t.protein_class || '—' }}</td>
              <td>{{ t.compounds.length }}</td>
              <td>{{ t.has_3d_structure ? 'Yes' : 'No' }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Literature tab -->
      <div v-if="tab === 'literature'" class="card">
        <table>
          <thead><tr><th>PMID</th><th>Gene</th></tr></thead>
          <tbody>
            <tr v-for="p in allPmids" :key="p.pmid + p.gene">
              <td><a :href="'https://pubmed.ncbi.nlm.nih.gov/' + p.pmid" target="_blank">{{ p.pmid }}</a></td>
              <td><router-link :to="'/target/' + p.gene">{{ p.gene }}</router-link></td>
            </tr>
          </tbody>
        </table>
        <div v-if="!allPmids.length" class="empty">No literature references</div>
      </div>

      <!-- Pathways tab -->
      <div v-if="tab === 'pathways'" class="card">
        <table>
          <thead><tr><th>Reactome ID</th><th>Name</th><th>Gene</th></tr></thead>
          <tbody>
            <tr v-for="p in allPathways" :key="p.reactome_id + p.gene">
              <td><a :href="'https://reactome.org/content/detail/' + p.reactome_id" target="_blank">{{ p.reactome_id }}</a></td>
              <td>{{ p.name }}</td>
              <td><router-link :to="'/target/' + p.gene">{{ p.gene }}</router-link></td>
            </tr>
          </tbody>
        </table>
        <div v-if="!allPathways.length" class="empty">No pathways data</div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import api from '../api/client.js'

const props = defineProps({ efoId: { type: String, required: true } })
const loading = ref(true)
const disease = ref(null)
const tab = ref('targets')

const allPmids = computed(() => {
  if (!disease.value) return []
  return disease.value.targets.flatMap(t =>
    t.pmids.map(pmid => ({ pmid, gene: t.gene_symbol }))
  )
})

const allPathways = computed(() => {
  if (!disease.value) return []
  return disease.value.targets.flatMap(t =>
    t.pathways.map(p => ({ ...p, gene: t.gene_symbol }))
  )
})

async function loadDisease() {
  loading.value = true
  try {
    disease.value = await api.getDisease(props.efoId)
  } catch (e) {
    console.error('Failed to load disease', e)
  } finally {
    loading.value = false
  }
}

onMounted(loadDisease)
watch(() => props.efoId, loadDisease)
</script>
