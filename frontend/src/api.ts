// API client for SDA Calculator backend
import axios from 'axios';
import type {
  CalculationRequest,
  CalculationResponse,
  OptionsResponse,
  BuildingTypeOption,
  SA4RegionOption,
} from './types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const api = {
  // Health check
  health: async (): Promise<{ status: string; database: string }> => {
    const response = await apiClient.get('/api/v1/health');
    return response.data;
  },

  // Calculate SDA pricing
  calculate: async (request: CalculationRequest): Promise<CalculationResponse> => {
    const response = await apiClient.post('/api/v1/sda/calculate', request);
    return response.data;
  },

  // Get options for dropdowns
  getOptions: async (params?: {
    stock_type?: string;
    building_type?: string;
  }): Promise<OptionsResponse> => {
    const response = await apiClient.get('/api/v1/sda/options', { params });
    return response.data;
  },

  // Get building types
  getBuildingTypes: async (stock_type?: string): Promise<BuildingTypeOption[]> => {
    const response = await apiClient.get('/api/v1/sda/building-types', {
      params: { stock_type },
    });
    return response.data;
  },

  // Get SA4 regions
  getRegions: async (): Promise<SA4RegionOption[]> => {
    const response = await apiClient.get('/api/v1/sda/regions');
    return response.data;
  },
};

export default api;
