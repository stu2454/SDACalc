"""
Database diagnostic script
Check what's in the database and help debug issues
"""
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add backend directory to path
import sys
sys.path.insert(0, '/app')

from models import BasePrice, LocationFactor, SA4Region, BuildingType, MRRCRate

# Database URL
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://sda_user:sda_password@db:5432/sda_calculator"
)

def diagnose_database():
    """Check database contents"""
    print("=" * 70)
    print("DATABASE DIAGNOSTIC")
    print("=" * 70)
    
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    
    try:
        # Check base prices
        print("\n1. BASE PRICES")
        total_prices = session.query(BasePrice).count()
        print(f"   Total records: {total_prices}")
        
        if total_prices > 0:
            # Count by stock type
            for stock_type in ['POST_2023', 'PRE_2023', 'EXISTING', 'LEGACY']:
                count = session.query(BasePrice).filter(
                    BasePrice.stock_type == stock_type
                ).count()
                print(f"   - {stock_type}: {count}")
            
            # Show sample
            print("\n   Sample record:")
            sample = session.query(BasePrice).first()
            print(f"   - Stock: {sample.stock_type}")
            print(f"   - Building: {sample.building_type}")
            print(f"   - Design: {sample.design_category}")
            print(f"   - Price: ${sample.price}")
        else:
            print("   ⚠️  NO PRICES FOUND!")
        
        # Check location factors
        print("\n2. LOCATION FACTORS")
        total_factors = session.query(LocationFactor).count()
        print(f"   Total records: {total_factors}")
        
        if total_factors > 0:
            # Count by stock category
            for category in ['NEW_BUILDS', 'OTHER']:
                count = session.query(LocationFactor).filter(
                    LocationFactor.stock_category == category
                ).count()
                print(f"   - {category}: {count}")
            
            # List unique regions with factors
            unique_regions = session.query(LocationFactor.sa4_region).distinct().all()
            print(f"\n   Regions with factors: {len(unique_regions)}")
            for region in unique_regions[:5]:
                print(f"   - {region[0]}")
            if len(unique_regions) > 5:
                print(f"   ... and {len(unique_regions) - 5} more")
        else:
            print("   ⚠️  NO LOCATION FACTORS FOUND!")
        
        # Check SA4 regions
        print("\n3. SA4 REGIONS")
        regions = session.query(SA4Region).all()
        print(f"   Total regions: {len(regions)}")
        print("\n   All regions:")
        for region in regions:
            print(f"   - {region.name} ({region.state})")
        
        # Check building types
        print("\n4. BUILDING TYPES")
        buildings = session.query(BuildingType).count()
        print(f"   Total building types: {buildings}")
        
        # Check MRRC rates
        print("\n5. MRRC RATES")
        mrrc = session.query(MRRCRate).first()
        if mrrc:
            print(f"   Single rate: ${mrrc.single_rate_fortnightly}/fortnight")
            print(f"   Couple rate: ${mrrc.couple_rate_fortnightly}/fortnight")
        else:
            print("   ⚠️  NO MRRC RATES FOUND!")
        
        # Test a calculation
        print("\n6. TEST CALCULATION")
        print("   Testing: POST_2023, Apartment 1br, FA, No OOA, No Sprinklers, ITC Claimed")
        
        test_price = session.query(BasePrice).filter(
            BasePrice.stock_type == 'POST_2023',
            BasePrice.building_type == 'Apartment, 1 bedroom, 1 resident',
            BasePrice.design_category == 'FA',
            BasePrice.ooa_status == 'NO_OOA',
            BasePrice.fire_sprinklers == False,
            BasePrice.itc_claimed == True
        ).first()
        
        if test_price:
            print(f"   ✓ Base price found: ${test_price.price}")
            
            # Try to find location factor for first region
            first_region = session.query(SA4Region).first()
            if first_region:
                print(f"   Testing with region: {first_region.name}")
                
                test_factor = session.query(LocationFactor).filter(
                    LocationFactor.sa4_region == first_region.name,
                    LocationFactor.stock_category == 'NEW_BUILDS',
                    LocationFactor.building_type_column == 1
                ).first()
                
                if test_factor:
                    print(f"   ✓ Location factor found: {test_factor.location_factor}")
                    annual = float(test_price.price) * float(test_factor.location_factor)
                    print(f"   ✓ Annual amount: ${annual:,.2f}")
                else:
                    print(f"   ⚠️  NO LOCATION FACTOR for {first_region.name}")
        else:
            print("   ⚠️  NO BASE PRICE FOUND!")
        
        print("\n" + "=" * 70)
        print("DIAGNOSTIC COMPLETE")
        print("=" * 70)
        
        # Recommendations
        print("\nRECOMMENDATIONS:")
        if total_prices == 0:
            print("⚠️  Run: python init_db.py")
        if total_factors == 0:
            print("⚠️  Run: python fix_location_factors.py")
        if total_prices > 0 and total_factors > 0:
            print("✓ Database looks good!")
        
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()

if __name__ == "__main__":
    diagnose_database()
