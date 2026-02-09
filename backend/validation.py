"""
Validation service for SDA calculator business rules
"""
from typing import List, Optional
from schemas import ValidationError


class ValidationService:
    """
    Validates SDA calculator input combinations according to NDIA rules
    """

    @staticmethod
    def validate_calculation_request(
        stock_type: str,
        building_type: str,
        design_category: str,
        ooa_status: str,
        allows_robust: bool
    ) -> List[ValidationError]:
        """
        Validate the complete calculation request
        Returns list of validation errors (empty if valid)
        """
        errors = []

        # Rule 1: Basic category only for Existing Stock
        if design_category == "BASIC" and stock_type != "EXISTING":
            errors.append(ValidationError(
                field="design_category",
                message="Basic design category is only available for Existing Stock"
            ))

        # Rule 2: Robust categories not available for Apartments
        if design_category in ["ROBUST", "ROBUST_BO"] and not allows_robust:
            errors.append(ValidationError(
                field="design_category",
                message="Robust design categories are not available for Apartments"
            ))

        # Rule 3: Basic only available without OOA
        if design_category == "BASIC" and ooa_status == "WITH_OOA":
            errors.append(ValidationError(
                field="ooa_status",
                message="Basic design category is only available without On-site Overnight Assistance"
            ))

        # Rule 4: Legacy stock building type validation
        if stock_type == "LEGACY" and not building_type.startswith("Legacy Stock"):
            errors.append(ValidationError(
                field="building_type",
                message="Legacy stock type requires Legacy Stock building types (6-10 residents)"
            ))

        return errors

    @staticmethod
    def get_available_design_categories(
        stock_type: str,
        building_type: str,
        allows_robust: bool
    ) -> List[dict]:
        """
        Get list of available design categories for given stock type and building type
        """
        categories = []

        # Basic only for Existing Stock
        if stock_type == "EXISTING":
            categories.append({
                "code": "BASIC",
                "name": "Basic",
                "ooa_available": ["NO_OOA"]
            })

        # Improved Liveability - always available
        categories.append({
            "code": "IL",
            "name": "Improved Liveability",
            "ooa_available": ["NO_OOA", "WITH_OOA"] if stock_type != "LEGACY" else ["NO_OOA"]
        })

        # Fully Accessible - always available
        categories.append({
            "code": "FA",
            "name": "Fully Accessible",
            "ooa_available": ["NO_OOA", "WITH_OOA"] if stock_type != "LEGACY" else ["NO_OOA"]
        })

        # Robust - not for Apartments
        if allows_robust:
            categories.append({
                "code": "ROBUST",
                "name": "Robust",
                "ooa_available": ["NO_OOA", "WITH_OOA"] if stock_type != "LEGACY" else ["NO_OOA"]
            })

            categories.append({
                "code": "ROBUST_BO",
                "name": "Robust with Breakout Room",
                "ooa_available": ["NO_OOA", "WITH_OOA"] if stock_type != "LEGACY" else ["NO_OOA"]
            })

        # High Physical Support - always available
        categories.append({
            "code": "HPS",
            "name": "High Physical Support",
            "ooa_available": ["NO_OOA", "WITH_OOA"] if stock_type != "LEGACY" else ["NO_OOA"]
        })

        return categories
