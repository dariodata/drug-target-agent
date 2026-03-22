<template>
  <div ref="container" class="graph-container"></div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch, toRaw } from 'vue'
import cytoscape from 'cytoscape'
import fcose from 'cytoscape-fcose'

cytoscape.use(fcose)

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
          'font-size': 11,
          color: '#bbb',
          'text-valign': 'bottom',
          'text-margin-y': 7,
          'background-color': (ele) => typeColors[ele.data('type')] || '#888',
          shape: (ele) => typeShapes[ele.data('type')] || 'ellipse',
          width: 34,
          height: 34,
          'border-width': 2,
          'border-color': (ele) => typeColors[ele.data('type')] || '#888',
          'border-opacity': 0.3,
          'text-max-width': 90,
          'text-wrap': 'ellipsis',
          'transition-property': 'width height border-width border-opacity opacity overlay-opacity',
          'transition-duration': 200,
        },
      },
      {
        selector: 'node.selected',
        style: {
          'border-width': 3,
          'border-color': '#fff',
          'border-opacity': 1,
          width: 44,
          height: 44,
          'overlay-padding': 8,
          'overlay-opacity': 0.12,
          'overlay-color': (ele) => typeColors[ele.data('type')] || '#fff',
          'font-size': 13,
          color: '#fff',
        },
      },
      {
        selector: 'node.highlighted',
        style: { 'border-width': 3, 'border-color': '#fff', 'border-opacity': 1, width: 38, height: 38 },
      },
      {
        selector: '.dimmed',
        style: { opacity: 0.1 },
      },
      {
        selector: 'edge',
        style: {
          width: 1.5,
          'line-color': '#3a3f4c',
          'target-arrow-color': '#3a3f4c',
          'target-arrow-shape': 'triangle',
          'curve-style': 'bezier',
          label: 'data(label)',
          'font-size': 7,
          color: '#555',
          'text-rotation': 'autorotate',
          'text-margin-y': -8,
          'transition-property': 'line-color target-arrow-color width opacity',
          'transition-duration': 200,
        },
      },
      {
        selector: 'edge.highlighted',
        style: {
          'line-color': '#6ea1e0',
          'target-arrow-color': '#6ea1e0',
          width: 2.5,
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

function centerNode(id) {
  if (!cy) return
  const node = cy.getElementById(id)
  if (!node || node.empty()) return

  cy.nodes().removeClass('selected')
  cy.elements().removeClass('dimmed highlighted')

  node.addClass('selected')
  const neighborhood = node.neighborhood().add(node)
  cy.elements().not(neighborhood).addClass('dimmed')
  neighborhood.edges().addClass('highlighted')

  cy.animate({
    center: { eles: node },
    zoom: Math.min(cy.zoom(), 2.5),
  }, {
    duration: 400,
    easing: 'ease-in-out-cubic',
  })
}

function clearSelection() {
  if (!cy) return
  cy.nodes().removeClass('selected')
  cy.elements().removeClass('dimmed highlighted')
}

defineExpose({ centerNode, clearSelection })

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
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
}
</style>
