<script setup lang="ts">
import {ref} from "vue";
import {VuePlotly} from "vue3-plotly";
import apiClient from './fonctions/api_client';
import Loader from './components/Loader.vue';

// Paramètres utilisateur
const temperature_ambiante = ref<number>(25);
const vitesse_vent = ref<number>(1);
const intensite_courant = ref<number>(300);
const temperature_cable_initiale = ref<number>(25);
const duree_minutes = ref<number>(30);

// Paramètres fixes
const simulation_duration_minutes = ref<number>(60);
const time_step_microsecond = ref<number>(0.1);

const loading = ref(false);
const result = ref<any>(null);
const error = ref<string | null>(null);

// Graphique
const graphData = ref<any[]>([]);
const graphLayout = ref<any>({
  title: "Évolution des températures finales",
  xaxis: {title: "Index (minutes)"},
  yaxis: {title: "Température (°C)"},
});

const envoyerSimulation = async () => {
  loading.value = true;
  result.value = null;
  error.value = null;
  graphData.value = [];

  try {
    result.value = await apiClient.simulateCableTemperatureConsumptionList({
      ambient_temperature: temperature_ambiante.value,
      wind_speed: vitesse_vent.value,
      current_intensity: intensite_courant.value,
      initial_cable_temperature: temperature_cable_initiale.value,
      simulation_duration_minutes: simulation_duration_minutes.value,
      time_step_microsecond: time_step_microsecond.value,
      duration_minutes: duree_minutes.value,
    });

    const tableau = [temperature_cable_initiale.value, ...result.value.final_temperature_list];

    graphData.value = [
      {
        x: tableau.map((_: number, i: number) => i),
        y: tableau,
        type: "scatter",
        mode: "lines+markers",
        name: "Températures finales",
        line: {color: "#0080ff"},
      },
      {
        x: [0],
        y: [tableau[0]],
        type: "scatter",
        mode: "markers",
        name: "Valeur initiale",
        marker: {color: "red", size: 10},
      },
    ];

    graphLayout.value.yaxis.title = result.value.final_temperature_unit || "°C";
  } catch (err: any) {
    error.value = err.message || "Erreur inconnue";
  } finally {
    loading.value = false;
  }
};
</script>

<template>
  <div class="container">
    <h1>Simulation Température Câble</h1>

    <form class="form-grid" @submit.prevent="envoyerSimulation">
      <div class="form-group">
        <label>Température ambiante</label>
        <input type="number" v-model="temperature_ambiante"/>
      </div>
      <div class="form-group">
        <label>Vitesse du vent</label>
        <input type="number" v-model="vitesse_vent"/>
      </div>
      <div class="form-group">
        <label>Intensité du courant</label>
        <input type="number" v-model="intensite_courant"/>
      </div>
      <div class="form-group">
        <label>Température initiale du câble</label>
        <input type="number" v-model="temperature_cable_initiale"/>
      </div>
      <div class="form-group">
        <label>Durée (minutes)</label>
        <input type="number" v-model="duree_minutes"/>
      </div>
      <div class="form-group">
        <label>Pas de recherche (seconde)</label>
        <input type="number" :value="simulation_duration_minutes"/>
      </div>
      <div class="form-group">
        <label>Pas de calcul (seconde)</label>
        <input type="number" :value="time_step_microsecond"/>
      </div>
    </form>

    <div class="actions">
      <button type="submit" @click="envoyerSimulation" :disabled="loading">
        Lancer la simulation
      </button>
    </div>

    <Loader v-if="loading"/>
    <div v-if="error" class="error">{{ error }}</div>

    <div v-if="result" class="result">
      <h2>Résultats</h2>

      <div class="block">
        <h3>🌡️ Températures finales ({{ result.final_temperature_unit }})</h3>
        <p>{{ result.final_temperature_list.join(", ") }}</p>
      </div>

      <div class="block">
        <h3>⚡ Énergie utilisée cumulée</h3>
        <p>{{ result.cumulative_energy_used }} {{ result.energy_used_unit }}</p>
      </div>

      <div class="block">
        <h3>💨 Émissions CO₂ cumulées</h3>
        <p>
          {{ result.cumulative_co2_emissions }} {{ result.co2_emissions_unit }}
        </p>
      </div>

      <div class="block">
        <h3>⏱️ Temps total d'exécution</h3>
        <p>
          {{ result.cumulative_execution_time }}
          {{ result.execution_time_unit }}
        </p>
      </div>

      <div class="block block-graphique">
        <h3>📈 Graphique des températures finales</h3>
        <VuePlotly :data="graphData" :layout="graphLayout"/>
      </div>
    </div>
  </div>
</template>

<style scoped>
.container {
  max-width: 1000px;
  margin: 2rem auto;
  padding: 2rem;
  background: #f9fafb;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

h1 {
  text-align: center;
  margin-bottom: 2rem;
  color: #2c3e50;
  font-size: 1.8rem;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
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

.actions {
  text-align: center;
  margin-top: 2rem;
}

.block-graphique h3 {
  text-align: center;
  margin-bottom: 10px;
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

.result {
  margin-top: 2rem;
  background-color: #ecf0f1;
  padding: 1rem;
  border-radius: 8px;
}

.block {
  margin-bottom: 1.5rem;
}

h3 {
  color: #2c3e50;
  margin-bottom: 0.5rem;
}

.error {
  margin-top: 1rem;
  color: red;
  font-weight: bold;
  text-align: center;
}

@keyframes l16 {
  100% {
    transform: rotate(1turn);
  }
}
</style>
