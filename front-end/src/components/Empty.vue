<script setup lang="ts">
import { defineProps } from "vue";

defineProps<{
  message: string | null;
}>();
</script>

<template>
  <div v-if="message" class="empty">{{ message }}</div>
</template>

<style scoped>
.empty {
  margin-top: 1rem;
  color: #6c757d;
  font-weight: bold;
  text-align: center;
  font-size: 1.2rem;
  background-color: #e9ecef;
  padding: 1rem;
  border: 1px solid #ced4da;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  animation: fadeIn 0.5s ease-in-out;
}
</style>