"""
Demand Forecasting Engine
Formula: Demand = Occupancy × BaseRate × SeasonalityFactor × CulturalBias × DisruptionFactor × WasteFeedback
"""

from datetime import date
from sqlalchemy.orm import Session
from models import Ingredient, Nationality, WasteLog, DisruptionEvent
import json

class ForecastEngine:
    """Calculates ingredient demand using multi-factor formula"""
    
    def __init__(self):
        self.waste_learning_rate = 0.15
    
    def calculate_demand(
        self,
        ingredient: Ingredient,
        occupancy: int,
        nationality: Nationality,
        date: date,
        db: Session
    ) -> float:
        """Calculate demand for an ingredient (kg)"""
        
        base_rate = ingredient.base_consumption_rate
        O = occupancy
        S = self._get_seasonality_factor(ingredient, date.month)
        C = self._get_cultural_factor(ingredient, nationality)
        D = self._get_disruption_factor(date, db)
        W = self._get_waste_adjustment(ingredient, db)
        
        demand = O * base_rate * S * C * D * W
        return max(0, demand)
    
    def _get_seasonality_factor(self, ingredient: Ingredient, month: int) -> float:
        """Return seasonality score"""
        if not ingredient.season:
            return 0.8
        
        # Parse JSON months
        try:
            months = json.loads(ingredient.season.months) if isinstance(ingredient.season.months, str) else ingredient.season.months
        except:
            return 0.8
        
        if month in months:
            return ingredient.season.score
        else:
            return 0.5
    
    def _get_cultural_factor(self, ingredient: Ingredient, nationality: Nationality) -> float:
        """Adjust based on nationality preferences"""
        ingredient_name_lower = ingredient.name.lower()
        
        if any(x in ingredient_name_lower for x in ["bread", "tabouna", "baguette"]):
            return nationality.bread_preference
        
        if any(x in ingredient_name_lower for x in ["milk", "yogurt", "cheese", "dairy"]):
            return nationality.dairy_preference
        
        if any(x in ingredient_name_lower for x in ["harissa", "spice", "pepper"]):
            return nationality.spice_tolerance
        
        return 1.0
    
    def _get_disruption_factor(self, target_date: date, db: Session) -> float:
        """Check for events that disrupt demand"""
        event = db.query(DisruptionEvent).filter(
            DisruptionEvent.occurred_at == target_date
        ).first()
        
        if event:
            return event.severity
        
        return 1.0
    
    def _get_waste_adjustment(self, ingredient: Ingredient, db: Session) -> float:
        """Reduce forecast if ingredient was frequently wasted"""
        recent_waste = db.query(WasteLog).filter(
            WasteLog.ingredient_id == ingredient.id
        ).order_by(WasteLog.date.desc()).limit(5).all()
        
        if not recent_waste:
            return 1.0
        
        avg_waste = sum(log.quantity_kg for log in recent_waste) / len(recent_waste)
        
        if avg_waste > (ingredient.base_consumption_rate * 0.2):
            return 1.0 - self.waste_learning_rate
        
        return 1.0
    
    def explain_forecast(
        self,
        ingredient: Ingredient,
        demand: float,
        occupancy: int,
        nationality: Nationality
    ) -> str:
        """Generate human-readable explanation"""
        
        explanation = f"Forecast for {ingredient.name}: {demand:.2f} {ingredient.unit}\n"
        explanation += f"- Base rate: {ingredient.base_consumption_rate} per person\n"
        explanation += f"- Occupancy: {occupancy} guests\n"
        explanation += f"- Nationality preference ({nationality.name}): affects bread/dairy/spice\n"
        
        if ingredient.season:
            explanation += f"- Seasonality: {ingredient.season.name} season\n"
        
        return explanation