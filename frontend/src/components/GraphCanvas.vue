<template>
  <div ref="container" class="graph-container"></div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch, toRaw } from 'vue'
import cytoscape from 'cytoscape'

const props = defineProps({
  graphData: { type: Object, default: () => ({ nodes: [], edges: [] }) },
  highlightIds: { type: Array, default: () => [] },
  layout: { type: String, default: 'cose' },
})

const emit = defineEmits(['node-click'])
const container = ref(null)
let cy = null
let observer = null

const typeColors = {
  disease: '#e74c3c', gene: '#3498db', protein: '#2ecc71',
  compound: '#f39c12', paper: '#9b59b6', pathway: '#1abc9c',
}

const typeShapes = {
  disease: 'diamond', gene: 'ellipse', protein: 'round-rectangle',
  compound: 'hexagon', paper: 'rectangle', pathway: 'triangle',
}

function buildCy() {
  if (!container.value) return
  if (cy) cy.destroy()

  const elements = [
    ...toRaw(props.graphData.nodes || []),
    ...toRaw(props.graphData.edges || []),
  ]

  cy = cytoscape({
    container: container.value,
    elements,
    style: [
      {
        selector: 'node',
        style: {
          label: 'data(label)',
          'font-size': 10,
          color: '#ccc',
          'text-valign': 'bottom',
          'text-margin-y': 6,
          'background-color': (ele) => typeColors[ele.data('type')] || '#888',
          shape: (ele) => typeShapes[ele.data('type')] || 'ellipse',
          width: 30,
          height: 30,
          'border-width': 0,
          'text-max-width': 80,
          'text-wrap': 'ellipsis',
        },
      },
      {
        selector: 'node.highlighted',
        style: { 'border-width': 3, 'border-color': '#fff', width: 38, height: 38 },
      },
      {
        selector: 'edge',
        style: {
          width: 1.5,
          'line-color': '#444',
          'target-arrow-color': '#444',
          'target-arrow-shape': 'triangle',
          'curve-style': 'bezier',
          label: 'data(label)',
          'font-size': 7,
          color: '#555',
          'text-rotation': 'autorotate',
          'text-margin-y': -8,
        },
      },
    ],
    layout: { name: props.layout, animate: false, nodeRepulsion: 8000, idealEdgeLength: 80 },
    minZoom: 0.2,
    maxZoom: 5,
  })

  cy.on('tap', 'node', (evt) => {
    emit('node-click', evt.target.data())
  })

  applyHighlights()
}

function applyHighlights() {
  if (!cy) return
  cy.nodes().removeClass('highlighted')
  if (props.highlightIds.length) {
    props.highlightIds.forEach((id) => {
      cy.getElementById(id).addClass('highlighted')
    })
  }
}

function runLayout() {
  if (!cy) return
  cy.layout({ name: props.layout, animate: true, animationDuration: 500, nodeRepulsion: 8000, idealEdgeLength: 80 }).run()
}

watch(() => props.graphData, buildCy, { deep: true })
watch(() => props.highlightIds, applyHighlights, { deep: true })
watch(() => props.layout, runLayout)

onMounted(() => {
  buildCy()
  observer = new ResizeObserver(() => { if (cy) cy.resize() })
  observer.observe(container.value)
})

onUnmounted(() => {
  if (observer) observer.disconnect()
  if (cy) cy.destroy()
})
</script>

<style scoped>
.graph-container {
  width: 100%;
  height: 100%;
  min-height: 300px;
}
</style>
