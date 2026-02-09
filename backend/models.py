"""
Database models for SDA Calculator
"""
from sqlalchemy import Column, Integer, String, Numeric, Boolean, Date, Index
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class BasePrice(Base):
    __tablename__ = "base_prices"

    id = Column(Integer, primary_key=True)
    stock_type = Column(String(20), nullable=False)
    building_type = Column(String(100), nullable=False)
    resident_count = Column(Integer, nullable=False)
    design_category = Column(String(20), nullable=False)
    ooa_status = Column(String(10), nullable=False)
    fire_sprinklers = Column(Boolean, nullable=False)
    itc_claimed = Column(Boolean, nullable=True)
    price = Column(Numeric(10, 2), nullable=False)
    effective_from = Column(Date, nullable=False)
    effective_to = Column(Date, nullable=True)

    __table_args__ = (
        Index('idx_base_price_lookup', 'stock_type', 'building_type', 'design_category', 
              'ooa_status', 'fire_sprinklers', 'itc_claimed', 'effective_from'),
    )


class LocationFactor(Base):
    __tablename__ = "location_factors"

    id = Column(Integer, primary_key=True)
    sa4_region = Column(String(100), nullable=False)
    stock_category = Column(String(20), nullable=False)  # NEW_BUILDS or OTHER
    building_type_column = Column(Integer, nullable=False)
    location_factor = Column(Numeric(5, 4), nullable=False)
    effective_from = Column(Date, nullable=False)
    effective_to = Column(Date, nullable=True)

    __table_args__ = (
        Index('idx_location_factor_lookup', 'sa4_region', 'stock_category', 
              'building_type_column', 'effective_from'),
    )


class MRRCRate(Base):
    __tablename__ = "mrrc_rates"

    id = Column(Integer, primary_key=True)
    effective_from = Column(Date, nullable=False)
    effective_to = Column(Date, nullable=True)
    single_rate_fortnightly = Column(Numeric(10, 2), nullable=False)
    couple_rate_fortnightly = Column(Numeric(10, 2), nullable=False)
    dsp_base = Column(Numeric(10, 2), nullable=False)
    pension_supplement = Column(Numeric(10, 2), nullable=False)
    cra_single = Column(Numeric(10, 2), nullable=False)
    cra_couple = Column(Numeric(10, 2), nullable=False)

    __table_args__ = (
        Index('idx_mrrc_effective', 'effective_from'),
    )


class BuildingType(Base):
    __tablename__ = "building_types"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    resident_count = Column(Integer, nullable=False)
    building_category = Column(String(50), nullable=False)  # Apartment, Villa, House, Group Home, Legacy
    allows_robust = Column(Boolean, nullable=False, default=True)
    location_factor_column = Column(Integer, nullable=False)
    display_order = Column(Integer, nullable=False)


class SA4Region(Base):
    __tablename__ = "sa4_regions"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    state = Column(String(10), nullable=False)
    display_order = Column(Integer, nullable=False)
