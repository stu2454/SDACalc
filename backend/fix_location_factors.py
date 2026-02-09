"""
Fix script: Generate location factors for all regions
Run this after initial database setup
"""
import os
from datetime import date
from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add backend directory to path
import sys
sys.path.insert(0, '/app')

from models import LocationFactor, SA4Region

# Database URL
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://sda_user:sda_password@db:5432/sda_calculator"
)

def fix_location_factors():
    """Generate location factors for all regions"""
    print("=" * 70)
    print("FIXING LOCATION FACTORS")
    print("=" * 70)
    
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    
    try:
        # Delete existing location factors
        print("\nDeleting existing location factors...")
        deleted = session.query(LocationFactor).delete()
        print(f"✓ Deleted {deleted} existing records")
        
        # Get all regions
        regions = session.query(SA4Region).all()
        print(f"\nFound {len(regions)} regions")
        
        if len(regions) == 0:
            print("ERROR: No regions found in database!")
            return
        
        # Generate location factors for each region
        count = 0
        for region in regions:
            # Create factors for both NEW_BUILDS and OTHER
            for stock_category in ["NEW_BUILDS", "OTHER"]:
                # Create factors for each building column (1-11)
                for column in range(1, 12):
                    # Assign realistic factors based on state
                    # Major cities get higher factors
                    if "Sydney" in region.name or "Melbourne" in region.name:
                        if "Inner" in region.name:
                            factor = Decimal("1.18")
                        else:
                            factor = Decimal("1.12")
                    elif "Brisbane" in region.name or "Perth" in region.name:
                        if "Inner" in region.name:
                            factor = Decimal("1.10")
                        else:
                            factor = Decimal("1.05")
                    elif "Adelaide" in region.name:
                        factor = Decimal("1.05")
                    elif region.state == "ACT":
                        factor = Decimal("1.08")
                    elif region.state in ["TAS", "NT"]:
                        factor = Decimal("1.00")
                    else:
                        factor = Decimal("1.05")
                    
                    lf = LocationFactor(
                        sa4_region=region.name,
                        stock_category=stock_category,
                        building_type_column=column,
                        location_factor=factor,
                        effective_from=date(2025, 7, 1),
                        effective_to=None
                    )
                    session.add(lf)
                    count += 1
        
        session.commit()
        print(f"\n✓ Created {count} location factors")
        
        # Verify
        print("\nVerifying location factors...")
        for region in regions[:3]:  # Check first 3
            factors = session.query(LocationFactor).filter(
                LocationFactor.sa4_region == region.name
            ).count()
            print(f"  {region.name}: {factors} factors")
        
        print("\n" + "=" * 70)
        print("LOCATION FACTORS FIXED SUCCESSFULLY")
        print("=" * 70)
        
    except Exception as e:
        print(f"\nError: {e}")
        session.rollback()
        raise
    finally:
        session.close()

if __name__ == "__main__":
    fix_location_factors()
