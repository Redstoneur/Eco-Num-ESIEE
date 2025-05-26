<script setup lang="ts">
import {defineProps, defineEmits} from "vue";
import FormTitle from "./FormTitle.vue";
import FormGroup from "./FormGroup.vue";
import FormSubmitButton from "./FormSubmitButton.vue";

defineProps<{
  title: string;
  temperature_ambiante_label: string;
  temperature_ambiante: number;
  vitesse_vent_label: string;
  vitesse_vent: number;
  intensite_courant_label: string;
  intensite_courant: number;
  temperature_cable_initiale_label: string;
  temperature_cable_initiale: number;
  duree_minutes_label: string;
  duree_minutes: number;
  simulation_duration_minutes_label: string;
  simulation_duration_minutes: number;
  time_step_label: string;
  time_step: number;
  buttonLabel: string;
  loading: boolean;
}>();

defineEmits([
  "submit",
  "update:temperature_ambiante",
  "update:vitesse_vent",
  "update:intensite_courant",
  "update:temperature_cable_initiale",
  "update:duree_minutes",
  "update:simulation_duration_minutes",
  "update:time_step",
]);
</script>

<template>
  <form class="form-grid" @submit.prevent="$emit('submit')">
    <FormTitle :title="title" />
    <FormGroup
        :label="temperature_ambiante_label"
        :modelValue="temperature_ambiante"
        @update:modelValue="(value) => $emit('update:temperature_ambiante', value)"
        type="number"
    />
    <FormGroup
        :label="vitesse_vent_label"
        :modelValue="vitesse_vent"
        @update:modelValue="(value) => $emit('update:vitesse_vent', value)"
        type="number"
    />
    <FormGroup
        :label="intensite_courant_label"
        :modelValue="intensite_courant"
        @update:modelValue="(value) => $emit('update:intensite_courant', value)"
        type="number"
    />
    <FormGroup
        :label="temperature_cable_initiale_label"
        :modelValue="temperature_cable_initiale"
        @update:modelValue="(value) => $emit('update:temperature_cable_initiale', value)"
        type="number"
    />
    <FormGroup
        :label="duree_minutes_label"
        :modelValue="duree_minutes"
        @update:modelValue="(value) => $emit('update:duree_minutes', value)"
        type="number"
    />
    <FormGroup
        :label="simulation_duration_minutes_label"
        :modelValue="simulation_duration_minutes"
        @update:modelValue="(value) => $emit('update:simulation_duration_minutes', value)"
        type="number"
    />
    <FormGroup
        :label="time_step_label"
        :modelValue="time_step"
        @update:modelValue="(value) => $emit('update:time_step', value)"
        type="number"
    />
    <FormSubmitButton :loading="loading" :label="buttonLabel" />
  </form>
</template>

<style scoped>
.form-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem;
  border: 1px solid #ccc;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

@media (max-width: 768px) {
  .form-grid >* {
    grid-column: span 3;
  }
}
</style>