<template>
  <div class="page">
    <div class="page-header">
      <h1>Compare Diseases</h1>
      <p>Discover shared drug targets across diseases</p>
    </div>

    <div class="card" style="margin-bottom: 24px;">
      <div style="display: flex; gap: 16px; align-items: end; flex-wrap: wrap;">
        <div>
          <label style="font-size: 12px; color: var(--text-dim); display: block; margin-bottom: 4px;">Disease 1</label>
          <select v-model="d1">
            <option value="">Select disease...</option>
            <option v-for="d in diseases" :key="d.efo_id" :value="d.efo_id">{{ d.name }}</option>
          </select>
        </div>
        <div>
          <label style="font-size: 12px; color: var(--text-dim); display: block; margin-bottom: 4px;">Disease 2</label>
          <select v-model="d2">
            <option value="">Select disease...</option>
            <option v-for="d in diseases" :key="d.efo_id" :value="d.efo_id">{{ d.name }}</option>
          </select>
        </div>
        <button class="btn btn-primary" :disabled="!d1 || !d2 || d1 === d2 || comparing" @click="runCompare">
          {{ comparing ? 'Comparing...' : 'Compare' }}
        </button>
      </div>
    </div>

    <div v-if="diseases.length < 2" class="card">
      <div class="empty">Load at least 2 diseases to use comparison. Currently {{ diseases.length }} loaded.</div>
    </div>

    <template v-if="result">
      <div class="card-grid" style="margin-bottom: 24px;">
        <div class="card stat-card">
          <div class="value" style="color: var(--accent);">{{ result.shared_targets.length }}</div>
          <div class="label">Shared Targets</div>
        </div>
        <div class="card stat-card">
          <div class="value" style="color: var(--disease);">{{ result.only_in_d1.length }}</div>
          <div class="label">Only in {{ result.disease_1.name }}</div>
        </div>
        <div class="card stat-card">
          <div class="value" style="color: var(--gene);">{{ result.only_in_d2.length }}</div>
          <div class="label">Only in {{ result.disease_2.name }}</div>
        </div>
      </div>

      <div v-if="result.shared_targets.length" class="card" style="margin-bottom: 24px;">
        <h3 style="margin-bottom: 16px;">Shared Targets</h3>
        <table>
          <thead>
            <tr>
              <th>Gene</th>
              <th>Name</th>
              <th>Score ({{ result.disease_1.name }})</th>
              <th>Score ({{ result.disease_2.name }})</th>
              <th>Protein Class</th>
              <th>Shared Pathways</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="t in result.shared_targets" :key="t.ensembl_id" class="clickable" @click="$router.push('/target/' + t.gene_symbol)">
              <td><router-link :to="'/target/' + t.gene_symbol">{{ t.gene_symbol }}</router-link></td>
              <td>{{ t.target_name }}</td>
              <td>
                <div class="score-bar"><div class="score-bar-fill" :style="{ width: (t.score_d1 * 100) + '%' }"></div></div>
                {{ t.score_d1?.toFixed(3) }}
              </td>
              <td>
                <div class="score-bar"><div class="score-bar-fill" :style="{ width: (t.score_d2 * 100) + '%' }"></div></div>
                {{ t.score_d2?.toFixed(3) }}
              </td>
              <td>{{ t.protein_class || '—' }}</td>
              <td>{{ t.shared_pathways.length }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px;">
        <div class="card">
          <h3 style="margin-bottom: 12px;">Only in {{ result.disease_1.name }}</h3>
          <div v-if="result.only_in_d1.length" style="display: flex; flex-wrap: wrap; gap: 6px;">
            <router-link v-for="g in result.only_in_d1" :key="g.ensembl_id" :to="'/target/' + g.gene_symbol"
              class="badge badge-gene">{{ g.gene_symbol }}</router-link>
          </div>
          <div v-else class="empty" style="min-height: 60px;">None</div>
        </div>
        <div class="card">
          <h3 style="margin-bottom: 12px;">Only in {{ result.disease_2.name }}</h3>
          <div v-if="result.only_in_d2.length" style="display: flex; flex-wrap: wrap; gap: 6px;">
            <router-link v-for="g in result.only_in_d2" :key="g.ensembl_id" :to="'/target/' + g.gene_symbol"
              class="badge badge-gene">{{ g.gene_symbol }}</router-link>
          </div>
          <div v-else class="empty" style="min-height: 60px;">None</div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../api/client.js'

const diseases = ref([])
const d1 = ref('')
const d2 = ref('')
const comparing = ref(false)
const result = ref(null)

async function runCompare() {
  comparing.value = true
  result.value = null
  try {
    result.value = await api.compare(d1.value, d2.value)
  } catch (e) {
    console.error('Comparison failed', e)
  } finally {
    comparing.value = false
  }
}

onMounted(async () => {
  try {
    diseases.value = await api.getDiseases()
  } catch (e) {
    console.error('Failed to load diseases', e)
  }
})
</script>
