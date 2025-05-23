<script setup lang="ts">
// Importation des dépendances
import {ref} from "vue";
import type {Data, Layout} from "plotly.js";

// Importation des composants
import Tile from "./components/Tile.vue";
import EnergyConsumptionDisplay from "./components/energy/EnergyConsumptionDisplay.vue";
import ProjectInfo from './components/ProjectInfo.vue';
import Formulaire from "./components/form/Formulaire.vue";
import Result from "./components/Result.vue";
import Loader from './components/Loader.vue';
import Error from './components/Error.vue';

// Importation des Fonctions
import apiClient, {
  type GlobalConsumptionResponse,
  type MultipleCableTemperatureConsumptionSimulationResponse
} from './fonctions/api_client';


// Propriétés du projet
const projectTitle = "Description du projet";
const projectDescription = "Ce projet est une application web interactive permettant de simuler la température d'un câble électrique en fonction de divers paramètres environnementaux et électriques. Il offre également des informations sur la consommation énergétique et les émissions de CO₂ associées aux simulations.";
const projectTitleUsage = "Comment utiliser l'application";
const usageSteps = [
  {
    title: "Paramètres de simulation",
    content: "Remplissez les champs du formulaire avec les valeurs souhaitées : Température ambiante, Vitesse du vent, etc.",
  },
  {
    title: "Lancer la simulation",
    content: "Cliquez sur le bouton **\"Lancer la simulation\"** pour démarrer la simulation.",
  },
  {
    title: "Résultats",
    content: "Une fois la simulation terminée, vous verrez les résultats et un graphique.",
  },
  {
    title: "Consommation globale",
    content: "La consommation énergétique et les émissions de CO₂ de toutes les simulations effectuées sont affichées en haut de la page.",
  },
];

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

// consommation globale des simulations sur toute la durée de fonctionnement des API
const global_consumption = ref<GlobalConsumptionResponse>(
    {
      energy_used: 0,
      energy_used_list: [],
      energy_used_unit: "kWh",
      co2_emissions: 0,
      co2_emissions_list: [],
      co2_emissions_unit: "kgCO2",
    }
);

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

const getGlobalConsumption = async () => {
  try {
    global_consumption.value = await apiClient.getGlobalConsumption();
  } catch (err: any) {
    error.value = err.message || "Erreur inconnue";
  }
};

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

    await getGlobalConsumption();
  } catch (err: any) {
    error.value = err.message || "Erreur inconnue";
  } finally {
    loading.value = false;
  }
};

// actualisation de la consommation globale au chargement de la page
getGlobalConsumption();

</script>

<template>
  <div class="container">
    <Tile title="Simulation Température Câble"/>

    <EnergyConsumptionDisplay
        title="Consommation pour toute les simulations"
        :energyUsed="global_consumption.energy_used"
        :energyUsedUnit="global_consumption.energy_used_unit"
        energyIcon="⚡"
        energyColor="#4CAF50"
        :co2Emissions="global_consumption.co2_emissions"
        :co2EmissionsUnit="global_consumption.co2_emissions_unit"
        co2Icon="💨"
        co2Color="#0080ff"
    />

    <ProjectInfo
        :title="projectTitle"
        :description="projectDescription"
        :titleUsage="projectTitleUsage"
        :usageSteps="usageSteps"
    />

    <Formulaire
        title="Paramètres de la simulation"
        temperature_ambiante_label="Température ambiante (°C)"
        v-model:temperature_ambiante="temperature_ambiante"
        vitesse_vent_label="Vitesse du vent (m/s)"
        v-model:vitesse_vent="vitesse_vent"
        intensite_courant_label="Intensité du courant (A)"
        v-model:intensite_courant="intensite_courant"
        temperature_cable_initiale_label="Température initiale du câble (°C)"
        v-model:temperature_cable_initiale="temperature_cable_initiale"
        duree_minutes_label="Nombre de minutes à simuler (min)"
        v-model:duree_minutes="duree_minutes"
        simulation_duration_minutes_label="Durée de la simulation (min)"
        v-model:simulation_duration_minutes="simulation_duration_minutes"
        time_step_label="Durée de la simulation pour une valeur suivante (s)"
        v-model:time_step="time_step_microsecond"
        buttonLabel="Lancer la simulation"
        :loading="loading"
        @submit="envoyerSimulation"
    />

    <Loader v-if="loading"/>
    <Error v-if="error" :error="error"/>
    <Result
        v-if="result"
        title="Résultats"
        paramsTitle="📝 Paramètres de la simulation"
        :params="{
          temperatureAmbiante: temperature_ambiante,
          vitesseVent: vitesse_vent,
          intensiteCourant: intensite_courant,
          temperatureCableInitiale: temperature_cable_initiale,
          dureeMinutes: duree_minutes,
          simulationDurationMinutes: simulation_duration_minutes,
          timeStep: time_step_microsecond
        }"
        temperatureTitle="🌡️ Températures finales"
        :temperature="{
          initial: {
            value: y[0],
             unit: result.final_temperature_unit
             },
          final: {
            value: y[y.length - 1],
             unit: result.final_temperature_unit
          }
        }"
        energyTitle="⚡ Énergie utilisée cumulée"
        :energy="{
          value: result.cumulative_energy_used,
          unit: result.energy_used_unit
        }"
        co2Title="💨 Émissions CO₂ cumulées"
        :co2="{
          value: result.cumulative_co2_emissions,
          unit: result.co2_emissions_unit
        }"
        executionTimeTitle="⏱️ Temps total d\'exécution"
        :executionTime="{
          value: result.cumulative_execution_time,
          unit: result.execution_time_unit
        }"
        graphTitle="📈 Graphique des températures finales"
        :graphData="graphData"
        :graphLayout="graphLayout"
    />


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
</style>
