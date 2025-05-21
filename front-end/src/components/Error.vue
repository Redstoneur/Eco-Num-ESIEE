<script setup lang="ts">
import { defineProps } from "vue";

defineProps<{
  error: string | null;
}>();
</script>

<template>
  <div v-if="error" class="error">{{ error }}</div>
</template>

<style scoped>
.error {
  margin-top: 1rem;
  color: red;
  font-weight: bold;
  text-align: center;
}
</style>