"""
Database initialization script
Creates tables and loads initial data
"""
import os
import sys
import csv
from datetime import date
from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models import Base, BasePrice, LocationFactor, MRRCRate, BuildingType, SA4Region

# Database URL
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://sda_user:sda_password@localhost:5432/sda_calculator"
)

def init_database():
    """Initialize database tables"""
    print("Creating database tables...")
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(engine)
    print("✓ Tables created")
    return engine

def load_building_types(session):
    """Load building types reference data"""
    print("\nLoading building types...")
    
    building_types = [
        # Apartments
        {"name": "Apartment, 1 bedroom, 1 resident", "resident_count": 1, "category": "Apartment", "allows_robust": False, "location_column": 1, "order": 1},
        {"name": "Apartment, 2 bedrooms, 1 resident", "resident_count": 1, "category": "Apartment", "allows_robust": False, "location_column": 2, "order": 2},
        {"name": "Apartment, 2 bedrooms, 2 residents", "resident_count": 2, "category": "Apartment", "allows_robust": False, "location_column": 3, "order": 3},
        {"name": "Apartment, 3 bedrooms, 2 residents", "resident_count": 2, "category": "Apartment", "allows_robust": False, "location_column": 4, "order": 4},
        # Villa/Duplex/Townhouse
        {"name": "Villa/Duplex/Townhouse, 1 resident", "resident_count": 1, "category": "Villa", "allows_robust": True, "location_column": 5, "order": 5},
        {"name": "Villa/Duplex/Townhouse, 2 residents", "resident_count": 2, "category": "Villa", "allows_robust": True, "location_column": 6, "order": 6},
        {"name": "Villa/Duplex/Townhouse, 3 residents", "resident_count": 3, "category": "Villa", "allows_robust": True, "location_column": 7, "order": 7},
        # House
        {"name": "House, 2 residents", "resident_count": 2, "category": "House", "allows_robust": True, "location_column": 8, "order": 8},
        {"name": "House, 3 residents", "resident_count": 3, "category": "House", "allows_robust": True, "location_column": 9, "order": 9},
        # Group Home
        {"name": "Group Home, 4 residents", "resident_count": 4, "category": "Group Home", "allows_robust": True, "location_column": 10, "order": 10},
        {"name": "Group Home, 5 residents", "resident_count": 5, "category": "Group Home", "allows_robust": True, "location_column": 11, "order": 11},
        # Legacy Stock
        {"name": "Legacy Stock, 6 residents", "resident_count": 6, "category": "Legacy", "allows_robust": True, "location_column": 11, "order": 12},
        {"name": "Legacy Stock, 7 residents", "resident_count": 7, "category": "Legacy", "allows_robust": True, "location_column": 11, "order": 13},
        {"name": "Legacy Stock, 8 residents", "resident_count": 8, "category": "Legacy", "allows_robust": True, "location_column": 11, "order": 14},
        {"name": "Legacy Stock, 9 residents", "resident_count": 9, "category": "Legacy", "allows_robust": True, "location_column": 11, "order": 15},
        {"name": "Legacy Stock, 10 residents", "resident_count": 10, "category": "Legacy", "allows_robust": True, "location_column": 11, "order": 16},
    ]
    
    for bt_data in building_types:
        bt = BuildingType(
            name=bt_data["name"],
            resident_count=bt_data["resident_count"],
            building_category=bt_data["category"],
            allows_robust=bt_data["allows_robust"],
            location_factor_column=bt_data["location_column"],
            display_order=bt_data["order"]
        )
        session.add(bt)
    
    session.commit()
    print(f"✓ Loaded {len(building_types)} building types")

def load_sa4_regions(session):
    """Load SA4 regions reference data"""
    print("\nLoading SA4 regions...")
    
    # Sample regions - in production, load all 89 from CSV
    regions = [
        ("NSW - Sydney - Inner City", "NSW", 1),
        ("NSW - Sydney - Eastern Suburbs", "NSW", 2),
        ("NSW - Sydney - Inner West", "NSW", 3),
        ("VIC - Melbourne - Inner", "VIC", 1),
        ("VIC - Melbourne - Inner East", "VIC", 2),
        ("VIC - Melbourne - North East", "VIC", 3),
        ("QLD - Brisbane - Inner City", "QLD", 1),
        ("QLD - Brisbane - North", "QLD", 2),
        ("SA - Adelaide - Central and Hills", "SA", 1),
        ("WA - Perth - Inner", "WA", 1),
        ("TAS - Hobart", "TAS", 1),
        ("NT - Darwin", "NT", 1),
        ("ACT - Australian Capital Territory", "ACT", 1),
    ]
    
    for name, state, order in regions:
        region = SA4Region(name=name, state=state, display_order=order)
        session.add(region)
    
    session.commit()
    print(f"✓ Loaded {len(regions)} SA4 regions")

def load_mrrc_rates(session):
    """Load MRRC rates"""
    print("\nLoading MRRC rates...")
    
    mrrc = MRRCRate(
        effective_from=date(2025, 3, 20),
        effective_to=None,
        single_rate_fortnightly=Decimal("506.56"),
        couple_rate_fortnightly=Decimal("320.98"),
        dsp_base=Decimal("1053.50"),
        pension_supplement=Decimal("81.60"),
        cra_single=Decimal("186.80"),
        cra_couple=Decimal("176.00")
    )
    session.add(mrrc)
    session.commit()
    print("✓ Loaded MRRC rates")

def load_base_prices_from_csv(session, csv_path):
    """Load base prices from CSV file"""
    print(f"\nLoading base prices from {csv_path}...")
    
    if not os.path.exists(csv_path):
        print(f"Warning: {csv_path} not found - skipping base prices")
        return
    
    count = 0
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            price = BasePrice(
                stock_type=row['stock_type'],
                building_type=row['building_type'],
                resident_count=int(row['resident_count']),
                design_category=row['design_category'],
                ooa_status=row['ooa_status'],
                fire_sprinklers=row['fire_sprinklers'].lower() == 'true',
                itc_claimed=None if row['itc_claimed'] == '' else (row['itc_claimed'].lower() == 'true'),
                price=Decimal(row['price']),
                effective_from=date(2025, 7, 1),
                effective_to=None
            )
            session.add(price)
            count += 1
            
            if count % 100 == 0:
                session.commit()
                print(f"  Loaded {count} prices...")
    
    session.commit()
    print(f"✓ Loaded {count} base prices")

def create_sample_location_factors(session):
    """Create sample location factors"""
    print("\nCreating sample location factors...")
    
    # Sample location factors for the regions we created
    # In production, load all from CSV
    regions = session.query(SA4Region).all()
    
    count = 0
    for region in regions:
        # Create factors for both NEW_BUILDS and OTHER
        for stock_category in ["NEW_BUILDS", "OTHER"]:
            # Create factors for each building column (1-11)
            for column in range(1, 12):
                # Sample factor based on state (just for demo)
                if region.state in ["NSW", "VIC"]:
                    factor = Decimal("1.15")
                elif region.state in ["QLD", "SA", "WA"]:
                    factor = Decimal("1.05")
                else:
                    factor = Decimal("1.00")
                
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
    print(f"✓ Created {count} location factors")

def main():
    """Main initialization function"""
    print("=" * 70)
    print("SDA CALCULATOR DATABASE INITIALIZATION")
    print("=" * 70)
    
    # Create tables
    engine = init_database()
    
    # Create session
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    
    try:
        # Load reference data
        load_building_types(session)
        load_sa4_regions(session)
        load_mrrc_rates(session)
        
        # Load pricing data from CSV
        csv_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'base_prices_complete.csv')
        load_base_prices_from_csv(session, csv_path)
        
        # Create sample location factors
        create_sample_location_factors(session)
        
        print("\n" + "=" * 70)
        print("DATABASE INITIALIZATION COMPLETE")
        print("=" * 70)
        
    except Exception as e:
        print(f"\nError during initialization: {e}")
        session.rollback()
        raise
    finally:
        session.close()

if __name__ == "__main__":
    main()
