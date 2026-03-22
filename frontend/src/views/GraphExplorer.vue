<template>
  <div class="explorer">
    <div class="toolbar">
      <div class="filters">
        <label v-for="t in nodeTypes" :key="t.key" class="filter-check">
          <input type="checkbox" v-model="t.visible" />
          <span :style="{ color: t.color }">{{ t.label }}</span>
        </label>
      </div>
      <select v-model="layoutName" class="layout-select">
        <option value="cose">Force-directed</option>
        <option value="circle">Circle</option>
        <option value="grid">Grid</option>
        <option value="breadthfirst">Hierarchy</option>
      </select>
      <button class="btn btn-primary" @click="sidebarOpen = !sidebarOpen">
        {{ sidebarOpen ? 'Hide Panel' : 'Show Panel' }}
      </button>
    </div>
    <div class="graph-area">
      <div v-if="loading" class="loading">Loading graph data...</div>
      <GraphCanvas
        v-else
        :graph-data="filteredGraph"
        :layout="layoutName"
        @node-click="onNodeClick"
      />
      <transition name="slide">
        <div v-if="sidebarOpen" class="sidebar card">
          <NodeDetail v-if="selectedNode" :node="selectedNode" />
          <div v-else class="sidebar-empty">Click a node to see details</div>
        </div>
      </transition>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import api from '../api/client.js'
import GraphCanvas from '../components/GraphCanvas.vue'
import NodeDetail from '../components/NodeDetail.vue'

const loading = ref(true)
const graphData = ref({ nodes: [], edges: [] })
const selectedNode = ref(null)
const sidebarOpen = ref(true)
const layoutName = ref('cose')

const nodeTypes = reactive([
  { key: 'disease', label: 'Diseases', color: '#e74c3c', visible: true },
  { key: 'gene', label: 'Genes', color: '#3498db', visible: true },
  { key: 'protein', label: 'Proteins', color: '#2ecc71', visible: true },
  { key: 'compound', label: 'Compounds', color: '#f39c12', visible: true },
  { key: 'paper', label: 'Papers', color: '#9b59b6', visible: true },
  { key: 'pathway', label: 'Pathways', color: '#1abc9c', visible: true },
])

const visibleTypes = computed(() => new Set(nodeTypes.filter(t => t.visible).map(t => t.key)))

const filteredGraph = computed(() => {
  const visNodes = graphData.value.nodes.filter(n => visibleTypes.value.has(n.data.type))
  const visIds = new Set(visNodes.map(n => n.data.id))
  const visEdges = graphData.value.edges.filter(e => visIds.has(e.data.source) && visIds.has(e.data.target))
  return { nodes: visNodes, edges: visEdges }
})

function onNodeClick(data) {
  selectedNode.value = data
  sidebarOpen.value = true
}

onMounted(async () => {
  try {
    graphData.value = await api.getGraph()
  } catch (e) {
    console.error('Failed to load graph', e)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.explorer { display: flex; flex-direction: column; flex: 1; overflow: hidden; }
.toolbar {
  display: flex; align-items: center; gap: 16px; padding: 8px 16px;
  background: var(--bg-card); border-bottom: 1px solid var(--border); flex-shrink: 0;
}
.filters { display: flex; gap: 12px; flex: 1; flex-wrap: wrap; }
.filter-check { display: flex; align-items: center; gap: 4px; font-size: 13px; cursor: pointer; }
.filter-check input { accent-color: currentColor; }
.layout-select { font-size: 13px; }
.graph-area { flex: 1; display: flex; position: relative; overflow: hidden; }
.graph-area .loading { position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; }
.sidebar {
  width: 320px; flex-shrink: 0; overflow-y: auto; border-left: 1px solid var(--border);
  border-radius: 0; background: var(--bg-card);
}
.sidebar-empty { padding: 24px; color: var(--text-dim); text-align: center; font-size: 14px; }
.slide-enter-active, .slide-leave-active { transition: width 0.2s, opacity 0.2s; }
.slide-enter-from, .slide-leave-to { width: 0; opacity: 0; overflow: hidden; }
</style>
