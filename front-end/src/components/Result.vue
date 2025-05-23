<script setup lang="ts">
import {defineProps} from 'vue';
import TwoDisplayValue from './Number/TwoDisplayValue.vue';
import DisplayValue from './Number/DisplayValue.vue';
import {VuePlotly} from 'vue3-plotly';
import type {Data, Layout} from "plotly.js";

defineProps<{
  title: string;
  paramsTitle: string;
  params: {
    temperatureAmbiante: number;
    vitesseVent: number;
    intensiteCourant: number;
    temperatureCableInitiale: number;
    dureeMinutes: number;
    simulationDurationMinutes: number;
    timeStep: number;
  };
  temperatureTitle: string;
  temperature: {
    initial: {
      value: number;
      unit: string;
    };
    final: {
      value: number;
      unit: string;
    };
  };
  energyTitle: string;
  energy: {
    value: number;
    unit: string;
  }
  co2Title: string;
  co2: {
    value: number;
    unit: string;
  }
  executionTimeTitle: string;
  executionTime: {
    value: number;
    unit: string;
  }
  graphTitle: string;
  graphData: Partial<Data>[];
  graphLayout: Partial<Layout>;
}>();
</script>

<template>
  <div class="result">
    <h2>{{ title }}</h2>

    <div class="result-block">
      <h3>{{ paramsTitle }}</h3>
      <ul>
        <li>Température ambiante : {{ params.temperatureAmbiante }} °C</li>
        <li>Vitesse du vent : {{ params.vitesseVent }} m/s</li>
        <li>Intensité du courant : {{ params.intensiteCourant }} A</li>
        <li>Température initiale du câble : {{ params.temperatureCableInitiale }} °C</li>
        <li>Nombre de minutes à simuler : {{ params.dureeMinutes }} min</li>
        <li>Durée de simulation pour une valeur suivante : {{ params.simulationDurationMinutes }} s</li>
        <li>Pas de temps pour la simulation : {{ params.timeStep }} s</li>
      </ul>
    </div>

    <div class="result-grid">
      <div class="result-grid-item">
        <h3>{{ temperatureTitle }}</h3>
        <TwoDisplayValue
            :x="temperature.initial.value"
            :y="temperature.final.value"
            :u1="temperature.initial.unit"
            :u2="temperature.final.unit"
        />
      </div>

      <div class="result-grid-item">
        <h3>{{ energyTitle }}</h3>
        <DisplayValue :value="energy.value" :unit="energy.unit"/>
      </div>

      <div class="result-grid-item">
        <h3>{{ co2Title }}</h3>
        <DisplayValue :value="co2.value" :unit="co2.unit"/>
      </div>

      <div class="result-grid-item">
        <h3>{{ executionTimeTitle }}</h3>
        <DisplayValue :value="executionTime.value" :unit="executionTime.unit"/>
      </div>
    </div>

    <div class="result-block result-block-graphique">
      <h3>{{ graphTitle }}</h3>
      <VuePlotly :data="graphData" :layout="graphLayout"/>
    </div>
  </div>
</template>

<style scoped>
.result {
  margin-top: 2rem;
  background-color: #ecf0f1;
  padding: 1rem;
  border-radius: 8px;
}

.result-block {
  margin-bottom: 1.5rem;
}

.result-block h3 {
  color: #2c3e50;
  margin-bottom: 0.5rem;
}

.result-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
  gap: 1rem;
  justify-items: center;
  align-items: center;
  width: 100%;
}

.result-grid-item {
  background: #f9fafb;
  padding: 1rem;
  border-radius: 8px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
  text-align: center;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

.result-grid-item h3 {
  margin-bottom: 0.5rem;
  color: #2c3e50;
}

.result-block-graphique h3 {
  text-align: center;
  margin-bottom: 10px;
}

/* Responsive */
@media (max-width: 900px) {
  .result-grid {
    flex-direction: column;
    align-items: stretch;
  }
  .result-grid-item {
    max-width: 100%;
    min-width: 0;
  }
}

@media (max-width: 600px) {
  .result {
    padding: 0.5rem;
  }
  .result-block {
    margin-bottom: 1rem;
  }
  .result-grid-item {
    padding: 0.5rem;
    font-size: 0.95rem;
  }
}
</style>