<script setup lang="ts">
import {defineProps, defineEmits} from "vue";

defineProps<{
  id: string;
  name: string;
  label: string;
  modelValue: number;
  min?: number;
  max?: number;
  step?: number;
}>();

defineEmits(["update:modelValue"]);
</script>

<template>
  <div class="form-group">
    <label :for="id">{{ label }}</label>
    <input
        :id="id"
        :name="name"
        type="number"
        :value="modelValue"
        :min="min !== undefined ? min : undefined"
        :max="max !== undefined ? max : undefined"
        :step="step !== undefined ? step : 'any'"
        @input="$emit('update:modelValue', Number(($event.target as HTMLInputElement)?.value))"
    />
  </div>
</template>

<style scoped>
.form-group {
  display: flex;
  flex-direction: column;
  margin-bottom: 1rem;
}

.form-group label {
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: #34495e;
}

.form-group input {
  padding: 0.6rem;
  border: 1px solid #ccc;
  border-radius: 8px;
  font-size: 1rem;
}

.form-group input:focus {
  border-color: #3498db;
  outline: none;
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.2);
}
</style>