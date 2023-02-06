<template>
  <v-app>
    <sidebar />

    <router-view />
  </v-app>
</template>

<script setup lang="ts">
import Sidebar from "@/components/Sidebar.vue";
</script>

<style lang="scss">
@import "@/styles/main.scss";
</style>
