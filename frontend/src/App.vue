<template>
  <div>
    <NavBar v-if="$route.meta.requiresAuth !== false" />
    <router-view />
  </div>
</template>

<script setup>
import NavBar from './components/NavBar.vue'
</script>