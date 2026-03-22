<template>
  <div class="explorer">
    <!-- Floating toolbar overlay -->
    <div class="toolbar-float">
      <div class="filter-group">
        <label v-for="t in nodeTypes" :key="t.key" class="filter-chip" :class="{ off: !t.visible }">
          <input type="checkbox" v-model="t.visible" />
          <span class="chip-dot" :style="{ background: t.color }"></span>
          <span class="chip-label">{{ t.label }}</span>
          <span class="chip-count">{{ countByType[t.key] || 0 }}</span>
        </label>
      </div>
      <div class="toolbar-controls">
        <select v-model="layoutName" class="layout-select">
          <option value="fcose">Force-directed</option>
          <option value="circle">Circle</option>
          <option value="grid">Grid</option>
          <option value="breadthfirst">Hierarchy</option>
          <option value="cose">CoSE (legacy)</option>
        </select>
      </div>
    </div>

    <!-- Split container: graph + panel -->
    <div class="split-container">
      <!-- Graph side -->
      <div
        class="graph-side"
        :style="{ flexBasis: panelOpen ? '60%' : '100%' }"
        @transitionend="onGraphTransitionEnd"
      >
        <div v-if="loading" class="loading">Loading graph data...</div>
        <GraphCanvas
          v-else
          ref="graphRef"
          :graph-data="filteredGraph"
          :layout="layoutName"
          @node-click="onNodeClick"
        />
      </div>

      <!-- Detail panel side -->
      <div
        class="panel-side"
        :style="{ flexBasis: panelOpen ? '40%' : '0%' }"
      >
        <DetailPanel
          v-if="panelOpen && selectedNode"
          :node="selectedNode"
          :nav-history="navHistory"
          @close="closePanel"
          @navigate="onPanelNavigate"
          @navigate-to="onBreadcrumbNavigate"
        />
      </div>
    </div>

    <!-- Node count indicator -->
    <div class="graph-info">
      {{ filteredGraph.nodes.length }} nodes &middot; {{ filteredGraph.edges.length }} edges
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import api from '../api/client.js'
import GraphCanvas from '../components/GraphCanvas.vue'
import DetailPanel from '../components/DetailPanel.vue'

const route = useRoute()
const loading = ref(true)
const graphData = ref({ nodes: [], edges: [] })
const layoutName = ref('fcose')

// Panel state
const panelOpen = ref(false)
const selectedNode = ref(null)
const navHistory = ref([])
const graphRef = ref(null)

const nodeTypes = reactive([
  { key: 'disease', label: 'Disease', color: 'var(--disease)', visible: true },
  { key: 'gene', label: 'Gene', color: 'var(--gene)', visible: true },
  { key: 'protein', label: 'Protein', color: 'var(--protein)', visible: true },
  { key: 'compound', label: 'Compound', color: 'var(--compound)', visible: true },
  { key: 'paper', label: 'Paper', color: 'var(--paper)', visible: true },
  { key: 'pathway', label: 'Pathway', color: 'var(--pathway)', visible: true },
])

const visibleTypes = computed(() => new Set(nodeTypes.filter(t => t.visible).map(t => t.key)))

const countByType = computed(() => {
  const counts = {}
  for (const n of graphData.value.nodes) {
    const t = n.data.type
    counts[t] = (counts[t] || 0) + 1
  }
  return counts
})

const filteredGraph = computed(() => {
  const visNodes = graphData.value.nodes.filter(n => visibleTypes.value.has(n.data.type))
  const visIds = new Set(visNodes.map(n => n.data.id))
  const visEdges = graphData.value.edges.filter(e => visIds.has(e.data.source) && visIds.has(e.data.target))
  return { nodes: visNodes, edges: visEdges }
})

function onNodeClick(data) {
  // Auto-enable node type filter if it's off
  const typeFilter = nodeTypes.find(t => t.key === data.type)
  if (typeFilter && !typeFilter.visible) {
    typeFilter.visible = true
  }

  selectedNode.value = data
  navHistory.value = [data]
  panelOpen.value = true

  nextTick(() => {
    graphRef.value?.centerNode(data.id)
  })
}

function onPanelNavigate(node) {
  // Auto-enable filter for navigated node type
  const typeFilter = nodeTypes.find(t => t.key === node.type)
  if (typeFilter && !typeFilter.visible) {
    typeFilter.visible = true
  }

  selectedNode.value = node
  navHistory.value.push(node)

  nextTick(() => {
    if (node.id) {
      graphRef.value?.centerNode(node.id)
    }
  })
}

function onBreadcrumbNavigate(index) {
  navHistory.value = navHistory.value.slice(0, index + 1)
  selectedNode.value = navHistory.value[navHistory.value.length - 1]

  nextTick(() => {
    if (selectedNode.value?.id) {
      graphRef.value?.centerNode(selectedNode.value.id)
    }
  })
}

function closePanel() {
  panelOpen.value = false
  selectedNode.value = null
  navHistory.value = []
  graphRef.value?.clearSelection()
}

function onGraphTransitionEnd(e) {
  // Only react to flex-basis transitions
  if (e.propertyName === 'flex-basis') {
    if (selectedNode.value?.id) {
      graphRef.value?.centerNode(selectedNode.value.id)
    }
  }
}

function onKeydown(e) {
  if (e.key === 'Escape' && panelOpen.value) {
    closePanel()
  }
}

onMounted(async () => {
  document.addEventListener('keydown', onKeydown)

  try {
    graphData.value = await api.getGraph()
  } catch (e) {
    console.error('Failed to load graph', e)
  } finally {
    loading.value = false
  }

  // Handle ?select=EFO_XXXX query param (from Dashboard links)
  await nextTick()
  const selectId = route.query.select
  if (selectId) {
    const node = graphData.value.nodes.find(n => n.data.id === selectId)
    if (node) {
      onNodeClick(node.data)
    }
  }
})

onUnmounted(() => {
  document.removeEventListener('keydown', onKeydown)
})
</script>

<style scoped>
.explorer {
  flex: 1;
  display: flex;
  flex-direction: column;
  position: relative;
  overflow: hidden;
  background:
    radial-gradient(ellipse at 20% 50%, rgba(91,156,245,0.03) 0%, transparent 60%),
    radial-gradient(ellipse at 80% 20%, rgba(0,212,170,0.02) 0%, transparent 50%),
    var(--bg);
}

/* ── Floating toolbar ── */
.toolbar-float {
  position: absolute;
  top: 12px;
  left: 12px;
  right: 12px;
  z-index: 20;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  pointer-events: none;
}
.toolbar-float > * { pointer-events: auto; }

.filter-group {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
  background: rgba(16,18,26,0.85);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 4px;
}

.filter-chip {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 11px;
  cursor: pointer;
  transition: opacity 0.15s, background 0.15s;
  user-select: none;
}
.filter-chip:hover { background: var(--bg-hover); }
.filter-chip.off { opacity: 0.35; }
.filter-chip input { display: none; }

.chip-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  flex-shrink: 0;
}
.chip-label { color: var(--text); font-weight: 500; }
.chip-count {
  color: var(--text-dim);
  font-family: var(--font-mono);
  font-size: 10px;
}

.toolbar-controls {
  display: flex;
  gap: 6px;
  background: rgba(16,18,26,0.85);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 4px;
}
.toolbar-controls .layout-select {
  font-size: 11px;
  padding: 4px 8px;
  background: transparent;
  border: none;
}

/* ── Split container ── */
.split-container {
  flex: 1;
  display: flex;
  min-height: 0;
  overflow: hidden;
}

.graph-side {
  position: relative;
  min-height: 0;
  min-width: 0;
  z-index: 1;
  flex-shrink: 0;
  transition: flex-basis 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.panel-side {
  min-width: 0;
  overflow: hidden;
  transition: flex-basis 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

/* ── Bottom info ── */
.graph-info {
  position: absolute;
  bottom: 12px;
  left: 12px;
  z-index: 20;
  font-size: 10px;
  font-family: var(--font-mono);
  color: var(--text-faint);
  background: rgba(16,18,26,0.7);
  padding: 3px 8px;
  border-radius: 4px;
  pointer-events: none;
}
</style>
