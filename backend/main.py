"""
SDA Calculator API
FastAPI application for NDIS Specialist Disability Accommodation pricing calculations
"""
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import Optional

from database import get_db
from schemas import (
    CalculationRequest, CalculationResponse, OptionsResponse,
    BuildingTypeOption, SA4RegionOption, ErrorResponse
)
from calculation import CalculationService
from validation import ValidationService
from models import BuildingType, SA4Region

# Create FastAPI app
app = FastAPI(
    title="SDA Calculator API",
    description="NDIS Specialist Disability Accommodation Pricing Calculator",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    """Health check endpoint"""
    return {
        "service": "SDA Calculator API",
        "status": "healthy",
        "version": "1.0.0"
    }


@app.get("/api/v1/health")
def health_check(db: Session = Depends(get_db)):
    """
    Health check with database connectivity test
    """
    try:
        # Test database connection
        db.execute("SELECT 1")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database unavailable: {str(e)}")


@app.post("/api/v1/sda/calculate", response_model=CalculationResponse)
def calculate_sda_pricing(
    request: CalculationRequest,
    db: Session = Depends(get_db)
):
    """
    Calculate SDA pricing for given parameters
    
    **Parameters:**
    - stock_type: POST_2023, PRE_2023, EXISTING, or LEGACY
    - building_type: Type of dwelling (e.g., "Apartment, 1 bedroom, 1 resident")
    - design_category: BASIC, IL, FA, ROBUST, ROBUST_BO, or HPS
    - ooa_status: NO_OOA or WITH_OOA
    - fire_sprinklers: true or false
    - itc_claimed: true/false (required for POST_2023, null for others)
    - sa4_region: SA4 region name (e.g., "NSW - Sydney - Inner City")
    
    **Returns:**
    - base_price: Annual base price before location adjustment
    - location_factor: Geographic multiplier
    - annual_sda_amount: Final annual SDA payment
    - mrrc: Maximum Reasonable Rent Contribution (single and couple)
    - net_ndia_single: Net NDIA payment for single occupancy
    - net_ndia_couple: Net NDIA payment for couple occupancy
    """
    try:
        # Get building type metadata for validation
        building = db.query(BuildingType).filter(
            BuildingType.name == request.building_type
        ).first()

        if not building:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid building type: {request.building_type}"
            )

        # Validate request
        validation_errors = ValidationService.validate_calculation_request(
            stock_type=request.stock_type,
            building_type=request.building_type,
            design_category=request.design_category,
            ooa_status=request.ooa_status,
            allows_robust=building.allows_robust
        )

        if validation_errors:
            raise HTTPException(
                status_code=400,
                detail=ErrorResponse(
                    detail="Validation failed",
                    errors=validation_errors
                ).dict()
            )

        # Perform calculation
        calc_service = CalculationService(db)
        result = calc_service.calculate(
            stock_type=request.stock_type,
            building_type=request.building_type,
            design_category=request.design_category,
            ooa_status=request.ooa_status,
            fire_sprinklers=request.fire_sprinklers,
            itc_claimed=request.itc_claimed,
            sa4_region=request.sa4_region
        )

        return result

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Calculation error: {str(e)}")


@app.get("/api/v1/sda/options", response_model=OptionsResponse)
def get_options(
    stock_type: Optional[str] = None,
    building_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get available options for form dropdowns
    
    **Query Parameters:**
    - stock_type (optional): Filter options by stock type
    - building_type (optional): Filter options by building type
    
    **Returns:**
    - stock_types: Available stock types
    - building_types: Available building types (filtered by stock_type if provided)
    - design_categories: Available design categories (filtered by stock_type and building_type if provided)
    - sa4_regions: All SA4 regions
    """
    response = OptionsResponse()

    # Stock types - always return all
    response.stock_types = ["POST_2023", "PRE_2023", "EXISTING", "LEGACY"]

    # Building types
    if stock_type:
        if stock_type == "LEGACY":
            # Legacy stock only has legacy building types
            buildings = db.query(BuildingType).filter(
                BuildingType.building_category == "Legacy"
            ).order_by(BuildingType.display_order).all()
        else:
            # Other stock types exclude legacy
            buildings = db.query(BuildingType).filter(
                BuildingType.building_category != "Legacy"
            ).order_by(BuildingType.display_order).all()
    else:
        # Return all building types
        buildings = db.query(BuildingType).order_by(
            BuildingType.display_order
        ).all()

    response.building_types = [
        BuildingTypeOption(
            name=b.name,
            resident_count=b.resident_count,
            allows_robust=b.allows_robust
        )
        for b in buildings
    ]

    # Design categories
    if stock_type and building_type:
        # Get building metadata
        building = db.query(BuildingType).filter(
            BuildingType.name == building_type
        ).first()

        if building:
            response.design_categories = ValidationService.get_available_design_categories(
                stock_type=stock_type,
                building_type=building_type,
                allows_robust=building.allows_robust
            )

    # SA4 regions
    regions = db.query(SA4Region).order_by(
        SA4Region.state, SA4Region.display_order
    ).all()

    response.sa4_regions = [
        SA4RegionOption(name=r.name, state=r.state)
        for r in regions
    ]

    return response


@app.get("/api/v1/sda/building-types", response_model=list[BuildingTypeOption])
def get_building_types(
    stock_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get building types, optionally filtered by stock type
    """
    if stock_type == "LEGACY":
        buildings = db.query(BuildingType).filter(
            BuildingType.building_category == "Legacy"
        ).order_by(BuildingType.display_order).all()
    elif stock_type:
        buildings = db.query(BuildingType).filter(
            BuildingType.building_category != "Legacy"
        ).order_by(BuildingType.display_order).all()
    else:
        buildings = db.query(BuildingType).order_by(
            BuildingType.display_order
        ).all()

    return [
        BuildingTypeOption(
            name=b.name,
            resident_count=b.resident_count,
            allows_robust=b.allows_robust
        )
        for b in buildings
    ]


@app.get("/api/v1/sda/regions", response_model=list[SA4RegionOption])
def get_regions(db: Session = Depends(get_db)):
    """
    Get all SA4 regions
    """
    regions = db.query(SA4Region).order_by(
        SA4Region.state, SA4Region.display_order
    ).all()

    return [
        SA4RegionOption(name=r.name, state=r.state)
        for r in regions
    ]
