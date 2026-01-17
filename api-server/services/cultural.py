"""
Cultural Intelligence Engine
Generates culturally-appropriate menus based on Tunisian terroir
"""

from sqlalchemy.orm import Session
from models import Dish, Ingredient, Season, Nationality
from typing import Optional, List
import json
from schemas import MenuDish, MenuResponse  # Make sure these exist in your schemas.py

class CulturalEngine:
    """Handles cultural food preferences and menu generation"""

    def generate_menu(
        self,
        month: int,
        nationality: Optional[str],
        db: Session
    ) -> MenuResponse:
        """
        Generate a culturally-appropriate seasonal menu
        """

        # Get all seasons
        all_seasons = db.query(Season).all()

        # Find season that contains this month
        season = None
        for s in all_seasons:
            try:
                months_list = json.loads(s.months) if isinstance(s.months, str) else s.months
                if month in months_list:
                    season = s
                    break
            except (json.JSONDecodeError, TypeError):
                continue

        # Get seasonal ingredients
        if not season:
            # Default to all-season items (staples)
            ingredients = db.query(Ingredient).filter(
                Ingredient.is_staple == True
            ).all()
        else:
            ingredients = db.query(Ingredient).filter(
                Ingredient.season_id == season.id
            ).all()

        # Get traditional dishes that use these ingredients
        dishes_list: List[MenuDish] = []
        for dish in db.query(Dish).filter(Dish.is_traditional == True).all():
            seasonal_match = any(
                ing.id in [si.id for si in ingredients] for ing in dish.ingredients
            )

            if seasonal_match or len(dish.ingredients) == 0:
                justification = self.justify_dish(dish, db)

                dishes_list.append(
                    MenuDish(
                        dish_id=int(dish.id),
                        dish_name=str(dish.name),
                        is_traditional=bool(dish.is_traditional),
                        seasonality_score=float(0.9 if seasonal_match else 0.5),
                        ingredients=[str(ing.name) for ing in dish.ingredients],
                        justification=[str(j) for j in justification]
                    )
                )

        # Cultural notes
        cultural_notes = self._get_cultural_notes(month, nationality)

        return MenuResponse(
            month=month,
            nationality=nationality,
            dishes=dishes_list,
            cultural_notes=cultural_notes
        )

    def justify_dish(self, dish: Dish, db: Session) -> List[str]:
        """
        Explain why a dish is recommended
        """
        reasons: List[str] = []

        if dish.is_traditional:
            reasons.append("Traditional Tunisian dish preserving culinary heritage")

        # Check seasonal ingredients
        seasonal_ingredients: List[Ingredient] = []
        for ing in dish.ingredients:
            if ing.season:
                try:
                    months_list = json.loads(ing.season.months) if isinstance(ing.season.months, str) else ing.season.months
                    if ing.season.score > 0.8:
                        seasonal_ingredients.append(ing)
                except (json.JSONDecodeError, TypeError, AttributeError):
                    continue

        if seasonal_ingredients:
            ing_names = ", ".join(ing.name for ing in seasonal_ingredients)
            reasons.append(f"Uses seasonal ingredients: {ing_names}")

        # Check local sourcing
        local_ingredients = [
            ing for ing in dish.ingredients
            if ing.supplier and ing.supplier.distance_km and ing.supplier.distance_km < 20
        ]
        if local_ingredients:
            reasons.append(f"Sources {len(local_ingredients)} ingredients locally")

        # Check cost efficiency
        affordable_ingredients = [
            ing for ing in dish.ingredients
            if ing.cost_per_unit < 5.0
        ]
        if len(dish.ingredients) > 0 and len(affordable_ingredients) / len(dish.ingredients) > 0.7:
            reasons.append("Cost-effective ingredients")

        if not reasons:
            reasons.append("Available year-round")

        return reasons

    def _get_cultural_notes(self, month: int, nationality: Optional[str]) -> str:
        """
        Provide cultural context for the menu
        """
        season_notes = {
            1: "Winter citrus season - perfect for fresh orange juice",
            2: "Late winter - hearty soups and stews tradition",
            3: "Spring arrives - fresh herbs and greens",
            4: "Spring abundance - artichokes and fava beans",
            5: "Late spring - lighter meals, more salads",
            6: "Summer heat - cold soups and fresh fruits",
            7: "Peak summer - watermelon and seafood season",
            8: "Late summer - grilled vegetables tradition",
            9: "Early autumn - date harvest in Tozeur",
            10: "Autumn - olive harvest and pressing season",
            11: "November - couscous friday tradition emphasized",
            12: "Winter - warm breakfast breads and honey"
        }

        note = season_notes.get(month, "")

        if nationality:
            nationality_map = {
                "FRA": "French guests typically prefer lighter breakfasts with pastries",
                "DEU": "German guests appreciate hearty bread selections",
                "ITA": "Italian guests value olive oil and fresh produce",
                "USA": "American guests enjoy variety and familiar options",
                "GBR": "British guests appreciate tea service and baked goods"
            }
            nat_note = nationality_map.get(nationality.upper(), "")
            if nat_note:
                note += f" | {nat_note}"

        return note

    def recommend_breakfast_items(
        self,
        nationality_code: str,
        db: Session
    ) -> List[str]:
        """
        Recommend breakfast items based on nationality
        """
        nationality = db.query(Nationality).filter(
            Nationality.code == nationality_code.upper()
        ).first()

        if not nationality:
            return ["Tabouna bread", "Olive oil", "Honey", "Fresh fruit"]

        recommendations: List[str] = ["Tabouna bread", "Olive oil", "Dates"]

        if nationality.bread_preference > 1.2:
            recommendations.append("Extra bread varieties")
        if nationality.dairy_preference > 1.2:
            recommendations.extend(["Yogurt", "Cheese selection"])
        if nationality.spice_tolerance > 1.2:
            recommendations.append("Harissa")
        else:
            recommendations.append("Mild condiments")

        if nationality.breakfast_style == "Continental":
            recommendations.extend(["Croissants", "Jam selection"])
        elif nationality.breakfast_style == "Mediterranean":
            recommendations.extend(["Olives", "Tomatoes", "Cucumber"])

        return recommendations
