<template>
  <div class="page">
    <div class="page-header">
      <h1>Dashboard</h1>
      <p v-if="!loading">{{ diseases.length }} diseases and {{ stats.genes || 0 }} gene targets in the knowledge graph</p>
      <p v-else>Loading overview...</p>
    </div>

    <div v-if="loading" class="loading">Loading...</div>
    <template v-else>
      <!-- Stats overview -->
      <section class="dash-section">
        <div class="section-label">Knowledge Graph</div>
        <StatsCards :stats="stats" />
      </section>

      <!-- Diseases as cards -->
      <section class="dash-section">
        <div class="section-label">Diseases</div>
        <div class="disease-grid" v-if="diseases.length">
          <router-link
            v-for="(d, i) in diseases"
            :key="d.efo_id"
            :to="{ path: '/', query: { select: d.efo_id } }"
            class="disease-card card"
            :style="{ '--i': i }"
          >
            <div class="disease-name">{{ d.name }}</div>
            <div class="disease-targets">
              <span class="target-count">{{ d.target_count }}</span>
              <span class="target-label">targets</span>
            </div>
            <div class="target-bar">
              <div class="target-bar-fill" :style="{ width: targetPercent(d) + '%' }"></div>
            </div>
          </router-link>
        </div>
        <div v-else class="card empty" style="min-height: 120px;">No diseases loaded yet. Run the pipeline to populate the knowledge graph.</div>
      </section>

      <!-- Cross-disease CTA -->
      <section class="dash-section" v-if="diseases.length >= 2">
        <router-link to="/compare" class="compare-cta card">
          <div>
            <h3>Cross-Disease Analysis</h3>
            <p>Compare {{ diseases.length }} diseases to discover shared drug targets and overlapping pathways.</p>
          </div>
          <span class="cta-arrow">&rarr;</span>
        </router-link>
      </section>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../api/client.js'
import StatsCards from '../components/StatsCards.vue'

const loading = ref(true)
const stats = ref({})
const diseases = ref([])

const maxTargets = computed(() => Math.max(...diseases.value.map(d => d.target_count), 1))

function targetPercent(d) {
  return (d.target_count / maxTargets.value) * 100
}

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

<style scoped>
.dash-section {
  margin-bottom: 28px;
}
.section-label {
  color: var(--text-dim);
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 12px;
  font-weight: 500;
}

/* Disease cards */
.disease-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 12px;
}
.disease-card {
  display: flex;
  flex-direction: column;
  gap: 8px;
  text-decoration: none;
  color: var(--text);
  border-left: 3px solid var(--disease);
  transition: border-color 0.15s, background 0.15s;
  animation: fadeInUp 0.35s ease both;
  animation-delay: calc(var(--i) * 0.06s);
}
.disease-card:hover {
  background: var(--bg-hover);
  color: var(--text);
}
.disease-name {
  font-weight: 600;
  font-size: 15px;
  letter-spacing: -0.2px;
}
.disease-targets {
  display: flex;
  align-items: baseline;
  gap: 6px;
}
.target-count {
  font-size: 24px;
  font-weight: 700;
  font-family: var(--font-mono);
  color: var(--disease);
  letter-spacing: -0.5px;
}
.target-label {
  font-size: 12px;
  color: var(--text-dim);
  text-transform: uppercase;
}
.target-bar {
  height: 3px;
  background: var(--border);
  border-radius: 2px;
  overflow: hidden;
}
.target-bar-fill {
  height: 100%;
  background: var(--disease);
  border-radius: 2px;
  transform-origin: left;
  animation: growBar 0.5s ease both;
  animation-delay: calc(var(--i) * 0.06s + 0.15s);
}
@keyframes growBar {
  from { transform: scaleX(0); }
  to { transform: scaleX(1); }
}

/* Compare CTA */
.compare-cta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  border-left: 3px solid var(--accent-warm);
  text-decoration: none;
  color: var(--text);
  transition: background 0.15s;
  animation: fadeInUp 0.35s ease both;
  animation-delay: 0.2s;
}
.compare-cta:hover {
  background: var(--bg-hover);
  color: var(--text);
}
.compare-cta h3 {
  color: var(--accent-warm);
  margin-bottom: 4px;
}
.compare-cta p {
  color: var(--text-dim);
  font-size: 13px;
}
.cta-arrow {
  font-size: 24px;
  color: var(--accent-warm);
  flex-shrink: 0;
}
</style>
