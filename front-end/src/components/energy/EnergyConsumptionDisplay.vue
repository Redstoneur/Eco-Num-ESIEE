<script setup lang="ts">
import EnergyDisplay from './EnergyDisplay.vue';

defineProps<{
  title: string;
  energyUsed: number;
  energyUsedUnit: string;
  energyIcon: string;
  energyColor: string;
  co2Emissions: number;
  co2EmissionsUnit: string;
  co2Icon: string;
  co2Color: string;
}>();
</script>

<template>
  <div class="energy-displays">
    <h3 class="energy-title">{{ title }}</h3>
    <div class="energy-displays-container">
      <EnergyDisplay
          class="energy-displays-container-item"
          :value="energyUsed"
          :unit="energyUsedUnit"
          :icon="energyIcon"
          :color="energyColor"
      />
      <EnergyDisplay
          class="energy-displays-container-item"
          :value="co2Emissions"
          :unit="co2EmissionsUnit"
          :icon="co2Icon"
          :color="co2Color"
      />
    </div>
  </div>
</template>

<style scoped>
.energy-displays {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 2rem;
}

.energy-title {
  font-size: 1.5rem;
  font-weight: bold;
  color: #2c3e50;
  margin-bottom: 1rem;
  text-align: center;
}

.energy-displays-container {
  display: flex;
  justify-content: space-around;
  margin-bottom: 2rem;
}

.energy-displays-container-item {
  margin: 0 1rem;
}
</style>