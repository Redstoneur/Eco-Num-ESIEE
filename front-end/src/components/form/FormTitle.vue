<script setup lang="ts">
import { defineProps } from "vue";

defineProps<{
  title: string;
}>();
</script>

<template>
  <h2 class="form-title">{{ title }}</h2>
</template>

<style scoped>
.form-title {
  grid-column: span 3;
  text-align: center;
  font-size: 1.5rem;
  color: #2c3e50;
  margin-bottom: 1rem;
}
</style>