"""
Pydantic schemas for API request/response validation
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from decimal import Decimal
from datetime import date


class CalculationRequest(BaseModel):
    stock_type: str = Field(..., pattern="^(POST_2023|PRE_2023|EXISTING|LEGACY)$")
    building_type: str
    design_category: str = Field(..., pattern="^(BASIC|IL|FA|ROBUST|ROBUST_BO|HPS)$")
    ooa_status: str = Field(..., pattern="^(NO_OOA|WITH_OOA)$")
    fire_sprinklers: bool
    itc_claimed: Optional[bool] = None
    sa4_region: str

    @field_validator('itc_claimed')
    def validate_itc_claimed(cls, v, info):
        stock_type = info.data.get('stock_type')
        if stock_type == 'POST_2023' and v is None:
            raise ValueError('itc_claimed is required for POST_2023 stock type')
        if stock_type != 'POST_2023' and v is not None:
            raise ValueError('itc_claimed only applicable to POST_2023 stock type')
        return v


class MRRCAmount(BaseModel):
    fortnightly: Decimal
    annual: Decimal


class MRRCBreakdown(BaseModel):
    single: MRRCAmount
    couple: MRRCAmount


class CalculationResponse(BaseModel):
    base_price: Decimal
    location_factor: Decimal
    annual_sda_amount: Decimal
    mrrc: MRRCBreakdown
    net_ndia_single: Decimal
    net_ndia_couple: Decimal
    effective_date: date


class DesignCategoryOption(BaseModel):
    code: str
    name: str
    ooa_available: List[str]


class BuildingTypeOption(BaseModel):
    name: str
    resident_count: int
    allows_robust: bool


class SA4RegionOption(BaseModel):
    name: str
    state: str


class OptionsResponse(BaseModel):
    stock_types: Optional[List[str]] = None
    building_types: Optional[List[BuildingTypeOption]] = None
    design_categories: Optional[List[DesignCategoryOption]] = None
    sa4_regions: Optional[List[SA4RegionOption]] = None


class ValidationError(BaseModel):
    field: str
    message: str


class ErrorResponse(BaseModel):
    detail: str
    errors: Optional[List[ValidationError]] = None
