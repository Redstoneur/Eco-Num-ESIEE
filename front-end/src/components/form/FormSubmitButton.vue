<script setup lang="ts">
import { defineProps } from "vue";

defineProps<{
  loading: boolean;
  label: string;
}>();
</script>

<template>
  <div class="actions">
    <button type="submit" :disabled="loading">
      {{ label }}
    </button>
  </div>
</template>

<style scoped>
.actions {
  grid-column: span 3;
  text-align: center;
  margin-top: 1rem;
}

button {
  padding: 0.8rem 2rem;
  background-color: #3498db;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  cursor: pointer;
  transition: background 0.3s;
}

button:hover {
  background-color: #2980b9;
}

button:disabled {
  background-color: #95a5a6;
  cursor: not-allowed;
}
</style>