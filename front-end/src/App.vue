<script setup lang="ts">
// Importation des dépendances
import {ref} from "vue";
import {VuePlotly} from "vue3-plotly";
import type {Data, Layout} from "plotly.js";

// Importation des composants
import Formulaire from "./components/form/Formulaire.vue";
import Loader from './components/Loader.vue';
import Error from './components/Error.vue';

// Importation des Fonctions
import apiClient, {type MultipleCableTemperatureConsumptionSimulationResponse} from './fonctions/api_client';

// Paramètres utilisateur
const temperature_ambiante = ref<number>(25);
const vitesse_vent = ref<number>(1);
const intensite_courant = ref<number>(300);
const temperature_cable_initiale = ref<number>(25);
const duree_minutes = ref<number>(30);
const simulation_duration_minutes = ref<number>(60);
const time_step_microsecond = ref<number>(0.1);

// Paramètres de simulation
const parametres = ref<{
  temperature_ambiante: number;
  vitesse_vent: number;
  intensite_courant: number;
  temperature_cable_initiale: number;
  duree_minutes: number;
  simulation_duration_minutes: number;
  time_step_microsecond: number;
}>();

const loading = ref(false);
const result = ref<MultipleCableTemperatureConsumptionSimulationResponse | null>(null);
const error = ref<string | null>(null);

// Graphique
const x = ref<number[]>([0]);
const y = ref<number[]>([0]);
const graphData = ref<Partial<Data>[]>([]);
const graphLayout = ref<Partial<Layout>>({
  title: {
    text: "Évolution des températures sur une période de temps",
    font: {size: 16},
  },
  xaxis: {
    title: {
      text: "Temps (secondes)",
      font: {size: 14},
    },
  },
  yaxis: {
    title: {
      text: "Température (°C)",
      font: {size: 14},
    },
  },
});

const envoyerSimulation = async () => {
  loading.value = true;
  result.value = null;
  error.value = null;
  graphData.value = [];

  try {
    // récupération des valeurs des paramètres
    parametres.value = {
      temperature_ambiante: temperature_ambiante.value,
      vitesse_vent: vitesse_vent.value,
      intensite_courant: intensite_courant.value,
      temperature_cable_initiale: temperature_cable_initiale.value,
      duree_minutes: duree_minutes.value,
      simulation_duration_minutes: simulation_duration_minutes.value,
      time_step_microsecond: time_step_microsecond.value,
    };

    // Appel de l'API pour simuler la consommation de température du câble
    result.value = await apiClient.simulateCableTemperatureConsumptionList({
      ambient_temperature: temperature_ambiante.value,
      wind_speed: vitesse_vent.value,
      current_intensity: intensite_courant.value,
      initial_cable_temperature: temperature_cable_initiale.value,
      simulation_duration_minutes: simulation_duration_minutes.value,
      time_step_microsecond: time_step_microsecond.value,
      duration_minutes: duree_minutes.value,
    });

    // Création des tableaux x et y pour le graphique
    x.value = [0, ...result.value.time_points_list];
    y.value = [temperature_cable_initiale.value, ...result.value.final_temperature_list];

    // Création des données pour le graphique
    graphData.value = [
      {
        x: x.value,
        y: y.value,
        type: "scatter",
        mode: "lines+markers",
        name: "Températures finales",
        line: {color: "#0080ff"},
      },
      {
        x: [x.value[0]],
        y: [y.value[0]],
        type: "scatter",
        mode: "markers",
        name: "Valeur initiale",
        marker: {color: "red", size: 10},
      },
      {
        x: [x.value[x.value.length - 1]],
        y: [y.value[y.value.length - 1]],
        type: "scatter",
        mode: "markers",
        name: "Valeur finale",
        marker: {color: "green", size: 10},
      },
    ];

    // Configuration du graphique
    graphLayout.value.title = {
      text: "Évolution des températures sur une période de temps"
    };
    if (graphLayout.value.xaxis) {
      graphLayout.value.xaxis.title = {
        text: `Temps (${result.value?.time_points_unit || "secondes"})`
      };
    }
    if (graphLayout.value.yaxis) {
      graphLayout.value.yaxis.title = {
        text: `Température (${result.value?.final_temperature_unit || "°C"})`
      };
    }
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

    <Formulaire
        v-model:temperature_ambiante="temperature_ambiante"
        v-model:vitesse_vent="vitesse_vent"
        v-model:intensite_courant="intensite_courant"
        v-model:temperature_cable_initiale="temperature_cable_initiale"
        v-model:duree_minutes="duree_minutes"
        v-model:simulation_duration_minutes="simulation_duration_minutes"
        v-model:time_step_microsecond="time_step_microsecond"
        :loading="loading"
        @submit="envoyerSimulation"
    />

    <Loader v-if="loading"/>
    <Error v-if="error" :error="error"/>

    <div v-if="result" class="result">
      <h2>Résultats</h2>

      <div class="block">
        <h3>📝 Paramètres de la simulation</h3>
        <ul>
          <li>Température ambiante : {{ temperature_ambiante }} °C</li>
          <li>Vitesse du vent : {{ vitesse_vent }} m/s</li>
          <li>Intensité du courant : {{ intensite_courant }} A</li>
          <li>Température initiale du câble : {{ temperature_cable_initiale }} °C</li>
          <li>Nombre de minutes à simuler : {{ duree_minutes }} min</li>
          <li>Durée de simulation pour une valeur suivante : {{ simulation_duration_minutes }} s</li>
          <li>Pas de temps pour la simulation : {{ time_step_microsecond }} s</li>
        </ul>
      </div>

      <div class="block">
        <h3>🌡️ Températures finales</h3>
        <p>
          {{ y[0] }} {{ result.final_temperature_unit }} - {{ y[y.length - 1] }} {{ result.final_temperature_unit }}
        </p>
      </div>

      <div class="block">
        <h3>⚡ Énergie utilisée cumulée</h3>
        <p>
          {{ result.cumulative_energy_used }}
          {{ result.energy_used_unit }}
        </p>
      </div>

      <div class="block">
        <h3>💨 Émissions CO₂ cumulées</h3>
        <p>
          {{ result.cumulative_co2_emissions }}
          {{ result.co2_emissions_unit }}
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

.block-graphique h3 {
  text-align: center;
  margin-bottom: 10px;
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
</style>
