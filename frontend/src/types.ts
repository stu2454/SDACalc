// Type definitions for SDA Calculator

export type StockType = 'POST_2023' | 'PRE_2023' | 'EXISTING' | 'LEGACY';
export type DesignCategory = 'BASIC' | 'IL' | 'FA' | 'ROBUST' | 'ROBUST_BO' | 'HPS';
export type OOAStatus = 'NO_OOA' | 'WITH_OOA';

export interface CalculationRequest {
  stock_type: StockType;
  building_type: string;
  design_category: DesignCategory;
  ooa_status: OOAStatus;
  fire_sprinklers: boolean;
  itc_claimed: boolean | null;
  sa4_region: string;
}

export interface MRRCAmount {
  fortnightly: number;
  annual: number;
}

export interface MRRCBreakdown {
  single: MRRCAmount;
  couple: MRRCAmount;
}

export interface CalculationResponse {
  base_price: number;
  location_factor: number;
  annual_sda_amount: number;
  mrrc: MRRCBreakdown;
  net_ndia_single: number;
  net_ndia_couple: number;
  effective_date: string;
}

export interface BuildingTypeOption {
  name: string;
  resident_count: number;
  allows_robust: boolean;
}

export interface DesignCategoryOption {
  code: DesignCategory;
  name: string;
  ooa_available: OOAStatus[];
}

export interface SA4RegionOption {
  name: string;
  state: string;
}

export interface OptionsResponse {
  stock_types?: StockType[];
  building_types?: BuildingTypeOption[];
  design_categories?: DesignCategoryOption[];
  sa4_regions?: SA4RegionOption[];
}

export interface ValidationError {
  field: string;
  message: string;
}

export interface ErrorResponse {
  detail: string;
  errors?: ValidationError[];
}
