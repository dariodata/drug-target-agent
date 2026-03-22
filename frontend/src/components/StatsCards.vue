<template>
  <div class="card-grid">
    <div v-for="item in items" :key="item.key" class="card stat-card">
      <div class="value" :style="{ color: item.color }">{{ stats[item.key] ?? 0 }}</div>
      <div class="label">{{ item.label }}</div>
    </div>
  </div>
</template>

<script setup>
defineProps({ stats: { type: Object, default: () => ({}) } })

const items = [
  { key: 'diseases', label: 'Diseases', color: '#e74c3c' },
  { key: 'genes', label: 'Genes', color: '#3498db' },
  { key: 'proteins', label: 'Proteins', color: '#2ecc71' },
  { key: 'compounds', label: 'Compounds', color: '#f39c12' },
  { key: 'papers', label: 'Papers', color: '#9b59b6' },
  { key: 'pathways', label: 'Pathways', color: '#1abc9c' },
]
</script>
