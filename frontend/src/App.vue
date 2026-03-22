<template>
  <div id="app">
    <nav class="navbar">
      <router-link to="/" class="logo">Drug Target Explorer</router-link>
      <div class="nav-links">
        <router-link to="/" exact-active-class="active">Graph</router-link>
        <router-link to="/dashboard" active-class="active">Dashboard</router-link>
        <router-link to="/compare" active-class="active">Compare</router-link>
      </div>
    </nav>
    <main>
      <router-view />
    </main>
  </div>
</template>

<script setup>
</script>
