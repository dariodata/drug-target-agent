<template>
  <div class="card-grid">
    <div v-for="(item, i) in items" :key="item.key" class="card stat-card" :style="{ borderTop: '2px solid ' + item.color, '--i': i }">
      <div class="value" :style="{ color: item.color }">{{ stats[item.key] ?? 0 }}</div>
      <div class="label">{{ item.label }}</div>
    </div>
  </div>
</template>

<script setup>
defineProps({ stats: { type: Object, default: () => ({}) } })

const items = [
  { key: 'diseases', label: 'Diseases', color: 'var(--disease)' },
  { key: 'genes', label: 'Genes', color: 'var(--gene)' },
  { key: 'proteins', label: 'Proteins', color: 'var(--protein)' },
  { key: 'compounds', label: 'Compounds', color: 'var(--compound)' },
  { key: 'papers', label: 'Papers', color: 'var(--paper)' },
  { key: 'pathways', label: 'Pathways', color: 'var(--pathway)' },
]
</script>

<style scoped>
.stat-card {
  animation: fadeInUp 0.35s ease both;
  animation-delay: calc(var(--i) * 0.06s);
}
</style>
