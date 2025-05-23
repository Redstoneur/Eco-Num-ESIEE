<script setup lang="ts">
import SmartNotation from './SmartNotation.vue';
import { defineProps } from 'vue';

defineProps<{
  value: number;
  unit?: string;
}>();
</script>

<template>
  <div class="display-value">
    <SmartNotation :value="value" />
    <span v-if="unit" class="unit"> {{ unit }}</span>
  </div>
</template>

<style scoped>
.display-value {
  display: flex;
  align-items: baseline;
  font-family: Arial, sans-serif;
}

.unit {
  margin-left: 4px;
  font-size: 0.9em;
  color: #555;
}
</style>