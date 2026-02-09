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

# Admin endpoints for initialization
import subprocess
import os


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


@app.get("/admin/init-database")
async def initialize_database(secret: str = ""):
    """Initialize database - call once after deployment"""
    if secret != "init2025":
        raise HTTPException(status_code=403, detail="Invalid secret")
    
    results = {"status": "running", "steps": []}
    
    try:
        # Check if already initialized
        session = SessionLocal()
        base_count = session.query(BasePrice).count()
        region_count = session.query(SA4Region).count()
        factor_count = session.query(LocationFactor).count()
        
        if base_count > 0 and region_count > 80 and factor_count > 1500:
            results["status"] = "already_initialized"
            results["data"] = {
                "base_prices": base_count,
                "regions": region_count,
                "location_factors": factor_count
            }
            session.close()
            return results
        session.close()
        
        # Install openpyxl
        results["steps"].append({"step": "install_openpyxl", "status": "running"})
        try:
            import openpyxl
            results["steps"][-1]["status"] = "already_installed"
        except ImportError:
            result = subprocess.run(["pip", "install", "openpyxl"], capture_output=True, text=True)
            results["steps"][-1]["status"] = "success" if result.returncode == 0 else "failed"
        
        # Run init_db.py
        results["steps"].append({"step": "init_db", "status": "running"})
        result = subprocess.run(["python", "init_db.py"], capture_output=True, text=True, cwd="/app")
        if result.returncode == 0:
            results["steps"][-1]["status"] = "success"
        else:
            raise Exception(f"init_db failed: {result.stderr}")
        
        # Load regions
        excel_path = "/data/SDA_Price_Calculator.xlsx"
        if os.path.exists(excel_path):
            results["steps"].append({"step": "load_regions", "status": "running"})
            result = subprocess.run(["python", "load_all_regions.py", excel_path], capture_output=True, text=True, cwd="/app")
            if result.returncode != 0:
                raise Exception(f"load_regions failed: {result.stderr}")
            results["steps"][-1]["status"] = "success"
            
            results["steps"].append({"step": "extract_factors", "status": "running"})
            result = subprocess.run(["python", "extract_location_factors.py", excel_path], capture_output=True, text=True, cwd="/app")
            if result.returncode != 0:
                raise Exception(f"extract_factors failed: {result.stderr}")
            results["steps"][-1]["status"] = "success"
        
        # Verify
        session = SessionLocal()
        stats = {
            "base_prices": session.query(BasePrice).count(),
            "regions": session.query(SA4Region).count(),
            "location_factors": session.query(LocationFactor).count()
        }
        session.close()
        
        results["status"] = "completed"
        results["final_stats"] = stats
        return results
        
    except Exception as e:
        results["status"] = "failed"
        results["error"] = str(e)
        return results

@app.get("/admin/db-status")
async def database_status():
    """Check database status"""
    session = SessionLocal()
    try:
        stats = {
            "base_prices": session.query(BasePrice).count(),
            "regions": session.query(SA4Region).count(),
            "location_factors": session.query(LocationFactor).count()
        }
        initialized = stats["base_prices"] > 800 and stats["regions"] > 80 and stats["location_factors"] > 1500
        return {
            "initialized": initialized,
            "stats": stats,
            "data_files": {
                "excel": os.path.exists("/data/SDA_Price_Calculator.xlsx"),
                "csv": os.path.exists("/data/base_prices_complete.csv")
            }
        }
    finally:
        session.close()