<script setup lang="ts">
import {defineProps, defineEmits} from "vue";
import FormTitle from "./FormTitle.vue";
import FormGroupNumber from "./FormGroupNumber.vue";
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
  number_of_repetition_label: string;
  number_of_repetition: number;
  simulation_duration_label: string;
  simulation_duration: number;
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
  "update:number_of_repetition",
  "update:simulation_duration",
  "update:time_step",
]);
</script>

<template>
  <form class="form-grid" @submit.prevent="$emit('submit')">
    <FormTitle :title="title"/>
    <FormGroupNumber
        id="temperature_ambiante"
        name="temperature_ambiante"
        :label="temperature_ambiante_label"
        :modelValue="temperature_ambiante"
        :min="-273.15"
        @update:modelValue="(value) => $emit('update:temperature_ambiante', value)"
    />
    <FormGroupNumber
        id="vitesse_vent"
        name="vitesse_vent"
        :label="vitesse_vent_label"
        :modelValue="vitesse_vent"
        :min="0"
        @update:modelValue="(value) => $emit('update:vitesse_vent', value)"
    />
    <FormGroupNumber
        id="intensite_courant"
        name="intensite_courant"
        :label="intensite_courant_label"
        :modelValue="intensite_courant"
        :min="0"
        @update:modelValue="(value) => $emit('update:intensite_courant', value)"
    />
    <FormGroupNumber
        id="temperature_cable_initiale"
        name="temperature_cable_initiale"
        :label="temperature_cable_initiale_label"
        :modelValue="temperature_cable_initiale"
        :min="-273.15"
        @update:modelValue="(value) => $emit('update:temperature_cable_initiale', value)"
    />
    <FormGroupNumber
        id="number_of_repetition"
        name="number_of_repetition"
        :label="number_of_repetition_label"
        :modelValue="number_of_repetition"
        :min="1"
        @update:modelValue="(value) => $emit('update:number_of_repetition', value)"
    />
    <FormGroupNumber
        id="simulation_duration"
        name="simulation_duration"
        :label="simulation_duration_label"
        :modelValue="simulation_duration"
        :min="1"
        @update:modelValue="(value) => $emit('update:simulation_duration', value)"
    />
    <FormGroupNumber
        class="latest"
        id="time_step"
        name="time_step"
        :label="time_step_label"
        :modelValue="time_step"
        :max="1"
        :min="0.000001"
        @update:modelValue="(value) => $emit('update:time_step', value)"
    />
    <FormSubmitButton :loading="loading" :label="buttonLabel"/>
  </form>
</template>

<style scoped>
.form-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem;
  border: 1px solid #ccc;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  padding: 1.5rem;
  justify-items: center;
  align-items: center;
}

.form-grid .latest {
  grid-column: span 3;
}

@media (max-width: 768px) {
  .form-grid > * {
    grid-column: span 3;
  }
}
</style>