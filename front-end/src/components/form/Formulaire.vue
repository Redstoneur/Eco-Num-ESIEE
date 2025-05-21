<script setup lang="ts">
import { defineProps, defineEmits } from "vue";
import FormGroup from "./FormGroup.vue";

defineProps<{
  temperature_ambiante: number;
  vitesse_vent: number;
  intensite_courant: number;
  temperature_cable_initiale: number;
  duree_minutes: number;
  simulation_duration_minutes: number;
  time_step_microsecond: number;
  loading: boolean;
}>();

const emit = defineEmits([
  "submit",
  "update:temperature_ambiante",
  "update:vitesse_vent",
  "update:intensite_courant",
  "update:temperature_cable_initiale",
  "update:duree_minutes",
  "update:simulation_duration_minutes",
  "update:time_step_microsecond",
]);
</script>

<template>
  <form class="form-grid" @submit.prevent="$emit('submit')">
    <FormGroup
        label="Température ambiante (°C)"
        :modelValue="temperature_ambiante"
        @update:modelValue="(value) => $emit('update:temperature_ambiante', value)"
        type="number"
    />
    <FormGroup
      label="Vitesse du vent (m/s)"
      :modelValue="vitesse_vent"
      @update:modelValue="(value) => $emit('update:vitesse_vent', value)"
      type="number"
    />
    <FormGroup
      label="Intensité du courant (A)"
      :modelValue="intensite_courant"
      @update:modelValue="(value) => $emit('update:intensite_courant', value)"
      type="number"
    />
    <FormGroup
      label="Température initiale du câble (°C)"
      :modelValue="temperature_cable_initiale"
      @update:modelValue="(value) => $emit('update:temperature_cable_initiale', value)"
      type="number"
    />
    <FormGroup
      label="Nombre de minutes à simuler (min)"
      :modelValue="duree_minutes"
      @update:modelValue="(value) => $emit('update:duree_minutes', value)"
      type="number"
    />
    <FormGroup
      label="Durée de la simulation pour une valeur suivante (s)"
      :modelValue="simulation_duration_minutes"
      @update:modelValue="(value) => $emit('update:simulation_duration_minutes', value)"
      type="number"
    />
    <FormGroup
      label="Pas de temps pour la simulation (s)"
      :modelValue="time_step_microsecond"
      @update:modelValue="(value) => $emit('update:time_step_microsecond', value)"
      type="number"
    />
    <div class="actions">
      <button type="submit" :disabled="loading">
        Lancer la simulation
      </button>
    </div>
  </form>
</template>

<style scoped>
.form-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem;
}

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