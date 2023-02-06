<template>
  <v-container fluid class="pa-0 fill-height">
    <v-navigation-drawer model-value rail permanent color="primary">
      <sidebar />
    </v-navigation-drawer>

    <v-main class="fill-height">
      <router-view />
    </v-main>
  </v-container>
</template>

<script lang="ts" setup>
import Sidebar from "@/components/Sidebar.vue";
</script>
