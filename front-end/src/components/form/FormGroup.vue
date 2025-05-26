<script setup lang="ts">
import { defineProps, defineEmits } from "vue";

defineProps<{
  id: string;
  name: string;
  label: string;
  modelValue: string | number;
  type?: string;
}>();

defineEmits(["update:modelValue"]);
</script>

<template>
  <div class="form-group">
    <label :for="id">{{ label }}</label>
    <input
      :id="id"
      :name="name"
      :type="type || 'text'"
      :value="modelValue"
      @input="$emit('update:modelValue', type === 'number' ? Number(($event.target as HTMLInputElement)?.value) : ($event.target as HTMLInputElement)?.value)"
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