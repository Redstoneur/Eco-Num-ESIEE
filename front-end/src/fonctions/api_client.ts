import axios from 'axios';
import type {AxiosInstance} from 'axios';

const apiClient: AxiosInstance = axios.create({
    baseURL: 'http://localhost:8000', // Remplacez par l'URL de votre serveur FastAPI
    headers: {
        'Content-Type': 'application/json',
    },
});

// Modèles de réponse
export interface RootResponse {
    message: string;
}

export interface HealthCheckResponse {
    status: string;
}

export interface CableTemperatureSimulationResponse {
    final_temperature: number;
    final_temperature_unit: string;
    execution_time: number;
    execution_time_unit: string;
}

export interface MultipleCableTemperatureSimulationResponse {
    final_temperature_list: number[];
    final_temperature_unit: string;
    execution_time: number[];
    cumulative_execution_time: number;
    execution_time_unit: string;
}

export interface CableTemperatureConsumptionSimulationResponse {
    final_temperature: number;
    final_temperature_unit: string;
    energy_used: number;
    energy_used_unit: string;
    co2_emissions: number;
    co2_emissions_unit: string;
    execution_time: number;
    execution_time_unit: string;
}

export interface MultipleCableTemperatureConsumptionSimulationResponse {
    final_temperature_list: number[];
    final_temperature_unit: string;
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
    // Root API
    async getRoot(): Promise<RootResponse> {
        const response = await apiClient.get<RootResponse>('/');
        return response.data;
    },

    // Health Check
    async getHealth(): Promise<HealthCheckResponse> {
        const response = await apiClient.get<HealthCheckResponse>('/health');
        return response.data;
    },

    // Simulation APIs
    async simulateCableTemperature(params: {
        ambient_temperature?: number;
        wind_speed?: number;
        current_intensity?: number;
        initial_cable_temperature?: number;
        simulation_duration_minutes?: number;
        time_step_microsecond?: number;
    }): Promise<CableTemperatureSimulationResponse> {
        let url = '/cable_temperature_simulation';
        url += '/?';
        if (params.ambient_temperature !== undefined) url += 'ambient_temperature=' + params.ambient_temperature + '&';
        if (params.wind_speed !== undefined) url += 'wind_speed=' + params.wind_speed + '&';
        if (params.current_intensity !== undefined) url += 'current_intensity=' + params.current_intensity + '&';
        if (params.initial_cable_temperature !== undefined) url += 'initial_cable_temperature=' + params.initial_cable_temperature + '&';
        if (params.simulation_duration_minutes !== undefined) url += 'simulation_duration_minutes=' + params.simulation_duration_minutes + '&';
        if (params.time_step_microsecond !== undefined) url += 'time_step_microsecond=' + params.time_step_microsecond + '&';

        if (url.endsWith('&')) {
            url = url.slice(0, -1);
        }

        const response = await apiClient.post<CableTemperatureSimulationResponse>(
            url
        );
        return response.data;
    },

    async simulateCableTemperatureList(params: {
        ambient_temperature?: number;
        wind_speed?: number;
        current_intensity?: number;
        initial_cable_temperature?: number;
        step_seconds?: number;
        step_microsecond?: number;
        duration_minutes?: number;
    }): Promise<MultipleCableTemperatureSimulationResponse> {
        let url = '/cable_temperature_simulation_list';
        url += '/?';
        if (params.ambient_temperature !== undefined) url += 'ambient_temperature=' + params.ambient_temperature + '&';
        if (params.wind_speed !== undefined) url += 'wind_speed=' + params.wind_speed + '&';
        if (params.current_intensity !== undefined) url += 'current_intensity=' + params.current_intensity + '&';
        if (params.initial_cable_temperature !== undefined) url += 'initial_cable_temperature=' + params.initial_cable_temperature + '&';
        if (params.step_seconds !== undefined) url += 'step_seconds=' + params.step_seconds + '&';
        if (params.step_microsecond !== undefined) url += 'step_microsecond=' + params.step_microsecond + '&';
        if (params.duration_minutes !== undefined) url += 'duration_minutes=' + params.duration_minutes + '&';

        if (url.endsWith('&')) {
            url = url.slice(0, -1);
        }

        const response = await apiClient.post<MultipleCableTemperatureSimulationResponse>(
            '/cable_temperature_simulation_list',
            params
        );
        return response.data;
    },

    async simulateCableTemperatureWithConsumption(params: {
        ambient_temperature?: number;
        wind_speed?: number;
        current_intensity?: number;
        initial_cable_temperature?: number;
        simulation_duration_minutes?: number;
        time_step_microsecond?: number;
    }): Promise<CableTemperatureConsumptionSimulationResponse> {
        let url = '/cable_temperature_consumption_simulation';
        url += '/?';
        if (params.ambient_temperature !== undefined) url += 'ambient_temperature=' + params.ambient_temperature + '&';
        if (params.wind_speed !== undefined) url += 'wind_speed=' + params.wind_speed + '&';
        if (params.current_intensity !== undefined) url += 'current_intensity=' + params.current_intensity + '&';
        if (params.initial_cable_temperature !== undefined) url += 'initial_cable_temperature=' + params.initial_cable_temperature + '&';
        if (params.simulation_duration_minutes !== undefined) url += 'simulation_duration_minutes=' + params.simulation_duration_minutes + '&';
        if (params.time_step_microsecond !== undefined) url += 'time_step_microsecond=' + params.time_step_microsecond + '&';

        if (url.endsWith('&')) {
            url = url.slice(0, -1);
        }

        const response = await apiClient.post<CableTemperatureConsumptionSimulationResponse>(
            url
        );
        return response.data;
    },

    async simulateCableTemperatureConsumptionList(params: {
        ambient_temperature?: number;
        wind_speed?: number;
        current_intensity?: number;
        initial_cable_temperature?: number;
        step_seconds?: number;
        step_microsecond?: number;
        duration_minutes?: number;
    }): Promise<MultipleCableTemperatureConsumptionSimulationResponse> {
        let url = '/cable_temperature_consumption_simulation_list';
        url += '/?';
        if (params.ambient_temperature !== undefined) url += 'ambient_temperature=' + params.ambient_temperature + '&';
        if (params.wind_speed !== undefined) url += 'wind_speed=' + params.wind_speed + '&';
        if (params.current_intensity !== undefined) url += 'current_intensity=' + params.current_intensity + '&';
        if (params.initial_cable_temperature !== undefined) url += 'initial_cable_temperature=' + params.initial_cable_temperature + '&';
        if (params.step_seconds !== undefined) url += 'step_seconds=' + params.step_seconds + '&';
        if (params.step_microsecond !== undefined) url += 'step_microsecond=' + params.step_microsecond + '&';
        if (params.duration_minutes !== undefined) url += 'duration_minutes=' + params.duration_minutes + '&';

        if (url.endsWith('&')) {
            url = url.slice(0, -1);
        }

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