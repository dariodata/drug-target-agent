<template>
  <div class="node-detail" v-if="node">
    <span :class="['badge', 'badge-' + node.type]">{{ node.type }}</span>
    <h3>{{ node.label }}</h3>

    <dl class="props">
      <template v-if="node.type === 'disease'">
        <dt>EFO ID</dt><dd>{{ node.id }}</dd>
      </template>
      <template v-if="node.type === 'gene'">
        <dt>Ensembl ID</dt><dd>{{ node.id }}</dd>
        <dt>Symbol</dt><dd>{{ node.label }}</dd>
        <dt v-if="node.name">Name</dt><dd v-if="node.name">{{ node.name }}</dd>
      </template>
      <template v-if="node.type === 'protein'">
        <dt>UniProt</dt><dd>{{ node.id }}</dd>
        <dt v-if="node.protein_class">Class</dt><dd v-if="node.protein_class">{{ node.protein_class }}</dd>
      </template>
      <template v-if="node.type === 'compound'">
        <dt>ChEMBL ID</dt><dd>{{ node.id }}</dd>
        <dt v-if="node.max_phase != null">Max Phase</dt>
        <dd v-if="node.max_phase != null"><span :class="'phase-pill phase-' + node.max_phase">Phase {{ node.max_phase }}</span></dd>
      </template>
      <template v-if="node.type === 'paper'">
        <dt>PMID</dt><dd>{{ node.id }}</dd>
        <dt v-if="node.title">Title</dt><dd v-if="node.title">{{ node.title }}</dd>
      </template>
      <template v-if="node.type === 'pathway'">
        <dt>Reactome ID</dt><dd>{{ node.id }}</dd>
        <dt v-if="node.label">Name</dt><dd v-if="node.label">{{ node.label }}</dd>
      </template>
    </dl>

    <div class="detail-link">
      <router-link v-if="node.type === 'disease'" :to="'/disease/' + node.id">View Disease Report</router-link>
      <router-link v-else-if="node.type === 'gene'" :to="'/target/' + node.label">View Gene Details</router-link>
      <a v-else-if="node.type === 'protein'" :href="'https://www.uniprot.org/uniprot/' + node.id" target="_blank">View on UniProt</a>
      <a v-else-if="node.type === 'compound'" :href="'https://www.ebi.ac.uk/chembl/compound_report_card/' + node.id" target="_blank">View on ChEMBL</a>
      <a v-else-if="node.type === 'paper'" :href="'https://pubmed.ncbi.nlm.nih.gov/' + node.id" target="_blank">View on PubMed</a>
      <a v-else-if="node.type === 'pathway'" :href="'https://reactome.org/content/detail/' + node.id" target="_blank">View on Reactome</a>
    </div>
  </div>
</template>

<script setup>
defineProps({ node: { type: Object, default: null } })
</script>

<style scoped>
.node-detail { padding: 16px; }
.node-detail h3 { margin: 12px 0 16px; font-size: 18px; }
.props { display: grid; grid-template-columns: auto 1fr; gap: 6px 12px; font-size: 13px; margin-bottom: 20px; }
.props dt { color: var(--text-dim); }
.props dd { margin: 0; word-break: break-all; }
.detail-link a {
  display: inline-block;
  padding: 6px 14px;
  background: var(--bg-hover);
  border-radius: var(--radius);
  font-size: 13px;
  color: var(--accent);
}
.detail-link a:hover { background: var(--border); }
</style>
