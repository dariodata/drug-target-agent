<template>
  <div class="detail-panel">
    <!-- Header -->
    <div class="panel-header">
      <button class="close-btn" @click="$emit('close')" title="Close (Esc)">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
          <path d="M18 6L6 18M6 6l12 12"/>
        </svg>
      </button>
      <span :class="['badge', 'badge-' + node.type]">{{ node.type }}</span>
      <span class="node-name">{{ node.label }}</span>
      <span v-if="node.name" class="secondary-label">{{ node.name }}</span>
    </div>

    <!-- Breadcrumb -->
    <div class="breadcrumb" v-if="navHistory.length > 1">
      <span class="crumb" @click="$emit('navigate-to', 0)">⌂</span>
      <template v-for="(item, i) in visibleCrumbs" :key="i">
        <span class="sep">›</span>
        <span v-if="item.collapsed" class="crumb" :title="collapsedTooltip">…</span>
        <span v-else-if="item.originalIndex === navHistory.length - 1" class="crumb current">{{ item.label }}</span>
        <span v-else class="crumb" @click="$emit('navigate-to', item.originalIndex)">{{ item.label }}</span>
      </template>
    </div>

    <!-- DetailContent handles tabs + content -->
    <DetailContent :node="node" @navigate="(n) => $emit('navigate', n)" />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import DetailContent from './DetailContent.vue'

const props = defineProps({
  node: { type: Object, required: true },
  navHistory: { type: Array, default: () => [] },
})

defineEmits(['close', 'navigate', 'navigate-to'])

const visibleCrumbs = computed(() => {
  const history = props.navHistory
  if (history.length <= 4) {
    return history.map((item, i) => ({ ...item, originalIndex: i }))
  }
  // Collapse middle items
  const first = { ...history[0], originalIndex: 0 }
  const collapsed = { collapsed: true }
  const secondLast = { ...history[history.length - 2], originalIndex: history.length - 2 }
  const last = { ...history[history.length - 1], originalIndex: history.length - 1 }
  return [first, collapsed, secondLast, last]
})

const collapsedTooltip = computed(() => {
  return props.navHistory.slice(1, -2).map(n => n.label).join(' › ')
})
</script>
