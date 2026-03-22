<template>
  <div class="page">
    <div class="page-header">
      <h1>Dashboard</h1>
      <p>Overview of the drug target knowledge graph</p>
    </div>

    <div v-if="loading" class="loading">Loading...</div>
    <template v-else>
      <StatsCards :stats="stats" />

      <div class="card" style="margin-top: 24px;">
        <h3 style="margin-bottom: 16px;">Diseases</h3>
        <table v-if="diseases.length">
          <thead>
            <tr>
              <th>Disease</th>
              <th>Targets</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="d in diseases" :key="d.efo_id" class="clickable" @click="$router.push({ path: '/', query: { select: d.efo_id } })">
              <td>{{ d.name }}</td>
              <td>{{ d.target_count }}</td>
              <td><router-link :to="{ path: '/', query: { select: d.efo_id } }" class="btn" style="font-size:12px; padding:4px 10px;">View</router-link></td>
            </tr>
          </tbody>
        </table>
        <div v-else class="empty">No diseases loaded yet</div>
      </div>

      <div v-if="diseases.length >= 2" class="card" style="margin-top: 24px;">
        <h3 style="margin-bottom: 8px;">Cross-Disease Analysis</h3>
        <p style="color: var(--text-dim); font-size: 14px;">
          You have {{ diseases.length }} diseases loaded.
          <router-link to="/compare">Compare diseases</router-link> to discover shared drug targets.
        </p>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../api/client.js'
import StatsCards from '../components/StatsCards.vue'

const loading = ref(true)
const stats = ref({})
const diseases = ref([])

onMounted(async () => {
  try {
    const [s, d] = await Promise.all([api.getStats(), api.getDiseases()])
    stats.value = s
    diseases.value = d
  } catch (e) {
    console.error('Failed to load dashboard', e)
  } finally {
    loading.value = false
  }
})
</script>
