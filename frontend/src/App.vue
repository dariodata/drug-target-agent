<template>
  <div id="app">
    <nav class="navbar">
      <router-link to="/" class="logo">Drug Target Explorer</router-link>
      <div class="nav-links">
        <router-link to="/" exact-active-class="active">Graph</router-link>
        <router-link to="/dashboard" active-class="active">Dashboard</router-link>
        <router-link to="/compare" active-class="active">Compare</router-link>
        <a href="https://www.arcosdiaz.com" target="_blank" rel="noopener">Blog</a>
      </div>
    </nav>
    <main>
      <router-view v-slot="{ Component }">
        <transition name="page" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>
    <footer class="site-footer">
      Built by Dario Arcos-Diaz
    </footer>
  </div>
</template>

<script setup>
</script>
