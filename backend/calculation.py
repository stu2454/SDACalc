"""
Calculation service for SDA pricing
"""
from decimal import Decimal
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Optional
from models import BasePrice, LocationFactor, MRRCRate, BuildingType
from schemas import CalculationResponse, MRRCAmount, MRRCBreakdown


class CalculationService:
    """
    Service for calculating SDA pricing
    """

    def __init__(self, db: Session):
        self.db = db

    def calculate(
        self,
        stock_type: str,
        building_type: str,
        design_category: str,
        ooa_status: str,
        fire_sprinklers: bool,
        itc_claimed: Optional[bool],
        sa4_region: str,
        calculation_date: date = None
    ) -> CalculationResponse:
        """
        Calculate SDA pricing
        """
        if calculation_date is None:
            calculation_date = date.today()

        # Step 1: Get base price
        base_price = self._get_base_price(
            stock_type=stock_type,
            building_type=building_type,
            design_category=design_category,
            ooa_status=ooa_status,
            fire_sprinklers=fire_sprinklers,
            itc_claimed=itc_claimed,
            calculation_date=calculation_date
        )

        if base_price is None:
            raise ValueError("No pricing found for this combination")

        # Step 2: Get location factor
        location_factor = self._get_location_factor(
            stock_type=stock_type,
            building_type=building_type,
            sa4_region=sa4_region,
            calculation_date=calculation_date
        )

        if location_factor is None:
            raise ValueError(f"No location factor found for region: {sa4_region}")

        # Step 3: Calculate annual SDA amount
        annual_sda_amount = round(Decimal(base_price.price) * Decimal(location_factor.location_factor), 0)

        # Step 4: Get MRRC rates
        mrrc_rate = self._get_mrrc_rate(calculation_date)

        if mrrc_rate is None:
            raise ValueError("No MRRC rates found for this date")

        # Step 5: Calculate MRRC annual amounts
        mrrc_single_annual = mrrc_rate.single_rate_fortnightly * 26
        mrrc_couple_annual = mrrc_rate.couple_rate_fortnightly * 26

        # Step 6: Calculate net NDIA payments
        net_ndia_single = annual_sda_amount - mrrc_single_annual
        net_ndia_couple = annual_sda_amount - mrrc_couple_annual

        return CalculationResponse(
            base_price=base_price.price,
            location_factor=location_factor.location_factor,
            annual_sda_amount=annual_sda_amount,
            mrrc=MRRCBreakdown(
                single=MRRCAmount(
                    fortnightly=mrrc_rate.single_rate_fortnightly,
                    annual=mrrc_single_annual
                ),
                couple=MRRCAmount(
                    fortnightly=mrrc_rate.couple_rate_fortnightly,
                    annual=mrrc_couple_annual
                )
            ),
            net_ndia_single=net_ndia_single,
            net_ndia_couple=net_ndia_couple,
            effective_date=base_price.effective_from
        )

    def _get_base_price(
        self,
        stock_type: str,
        building_type: str,
        design_category: str,
        ooa_status: str,
        fire_sprinklers: bool,
        itc_claimed: Optional[bool],
        calculation_date: date
    ) -> Optional[BasePrice]:
        """
        Lookup base price from database
        """
        query = self.db.query(BasePrice).filter(
            and_(
                BasePrice.stock_type == stock_type,
                BasePrice.building_type == building_type,
                BasePrice.design_category == design_category,
                BasePrice.ooa_status == ooa_status,
                BasePrice.fire_sprinklers == fire_sprinklers,
                BasePrice.effective_from <= calculation_date,
                (BasePrice.effective_to.is_(None) | (BasePrice.effective_to > calculation_date))
            )
        )

        # Handle ITC claimed logic
        if stock_type == "POST_2023":
            query = query.filter(BasePrice.itc_claimed == itc_claimed)
        elif stock_type == "PRE_2023":
            # Pre-2023 always uses ITC claimed pricing
            query = query.filter(BasePrice.itc_claimed == True)
        else:
            # Existing and Legacy stock have NULL itc_claimed
            query = query.filter(BasePrice.itc_claimed.is_(None))

        return query.first()

    def _get_location_factor(
        self,
        stock_type: str,
        building_type: str,
        sa4_region: str,
        calculation_date: date
    ) -> Optional[LocationFactor]:
        """
        Lookup location factor from database
        """
        # Determine stock category
        if stock_type in ["POST_2023", "PRE_2023"]:
            stock_category = "NEW_BUILDS"
        else:
            stock_category = "OTHER"

        # Get building type column index
        building = self.db.query(BuildingType).filter(
            BuildingType.name == building_type
        ).first()

        if not building:
            return None

        # For Legacy stock, always use column 11
        if stock_type == "LEGACY":
            building_type_column = 11
        else:
            building_type_column = building.location_factor_column

        return self.db.query(LocationFactor).filter(
            and_(
                LocationFactor.sa4_region == sa4_region,
                LocationFactor.stock_category == stock_category,
                LocationFactor.building_type_column == building_type_column,
                LocationFactor.effective_from <= calculation_date,
                (LocationFactor.effective_to.is_(None) | (LocationFactor.effective_to > calculation_date))
            )
        ).first()

    def _get_mrrc_rate(self, calculation_date: date) -> Optional[MRRCRate]:
        """
        Lookup MRRC rate from database
        """
        return self.db.query(MRRCRate).filter(
            and_(
                MRRCRate.effective_from <= calculation_date,
                (MRRCRate.effective_to.is_(None) | (MRRCRate.effective_to > calculation_date))
            )
        ).first()
