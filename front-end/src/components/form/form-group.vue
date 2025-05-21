<script setup lang="ts">
import { defineProps } from "vue";

defineProps<{
  label: string;
  modelValue: string | number;
  type?: string;
}>();

const emit = defineEmits(["update:modelValue"]);
</script>

<template>
  <div class="form-group">
    <label>{{ label }}</label>
    <input
      :type="type || 'text'"
      :value="modelValue"
      @input="$emit('update:modelValue', ($event.target as HTMLInputElement)?.value)"
    />
  </div>
</template>

<style scoped>
.form-group {
  display: flex;
  flex-direction: column;
  margin-bottom: 1rem;
}

label {
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: #34495e;
}

input {
  padding: 0.6rem;
  border: 1px solid #ccc;
  border-radius: 8px;
  font-size: 1rem;
}

input:focus {
  border-color: #3498db;
  outline: none;
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.2);
}
</style>