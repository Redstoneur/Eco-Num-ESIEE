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
  font-size: 1.2rem;
  background-color: #f8d7da;
  padding: 1rem;
  border: 1px solid #f5c6cb;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  animation: fadeIn 0.5s ease-in-out;
}
</style>