import type {AxiosInstance} from 'axios';
import axios from 'axios';

const apiClient: AxiosInstance = axios.create({
    baseURL: 'http://localhost:8000', // Remplacez par l'URL de votre serveur FastAPI
    headers: {
        'Content-Type': 'application/json',
    },
});

// Modèles de réponse
export interface MultipleCableTemperatureConsumptionSimulationResponse {
    final_temperature_list: number[];
    final_temperature_unit: string;
    time_points_list: number[];
    time_points_unit: string;
    energy_used_list: number[];
    cumulative_energy_used: number;
    energy_used_unit: string;
    co2_emissions_list: number[];
    cumulative_co2_emissions: number;
    co2_emissions_unit: string;
    execution_time: number[];
    cumulative_execution_time: number;
    execution_time_unit: string;
}

export interface GlobalConsumptionResponse {
    energy_used: number;
    energy_used_list: number[];
    energy_used_unit: string;
    co2_emissions: number;
    co2_emissions_list: number[];
    co2_emissions_unit: string;
}

// API Client
export default {
    async simulateCableTemperatureConsumptionList(params: {
        ambient_temperature?: number;
        wind_speed?: number;
        current_intensity?: number;
        initial_cable_temperature?: number;
        number_of_repetition?: number;
        time_step?: number;
        simulation_duration?: number;
    }): Promise<MultipleCableTemperatureConsumptionSimulationResponse> {
        let url = '/cable_temperature_consumption_simulation_list';
        url += '?';
        if (params.ambient_temperature !== undefined) url += 'ambient_temperature=' + params.ambient_temperature + '&';
        if (params.wind_speed !== undefined) url += 'wind_speed=' + params.wind_speed + '&';
        if (params.current_intensity !== undefined) url += 'current_intensity=' + params.current_intensity + '&';
        if (params.initial_cable_temperature !== undefined) url += 'initial_cable_temperature=' + params.initial_cable_temperature + '&';
        if (params.number_of_repetition !== undefined) url += 'number_of_repetition=' + params.number_of_repetition + '&';
        if (params.time_step !== undefined) url += 'time_step=' + params.time_step + '&';
        if (params.simulation_duration !== undefined) url += 'simulation_duration=' + params.simulation_duration + '&';

        if (url.endsWith('&')) {
            url = url.slice(0, -1);
        }

        // Uncomment the line below to log the URL for debugging purposes
        // console.log('API URL:', url);

        const response = await apiClient.post(
            url
        );

        return response.data;
    },

    // Global Consumption APIs
    async getGlobalConsumption(): Promise<GlobalConsumptionResponse> {
        const response = await apiClient.get<GlobalConsumptionResponse>('/global_consumption');
        return response.data;
    },

    async resetGlobalConsumption(): Promise<GlobalConsumptionResponse> {
        const response = await apiClient.post<GlobalConsumptionResponse>('/reset_global_consumption');
        return response.data;
    },
};
