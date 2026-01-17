"""
Waste Analysis Service
Analyzes waste patterns and provides recommendations
"""

from sqlalchemy.orm import Session
from sqlalchemy import func
from models import WasteLog, Ingredient
from typing import List
from collections import defaultdict

class WasteAnalyzer:
    """Analyzes food waste and provides actionable insights"""
    
    def analyze(self, waste_logs: List[WasteLog], db: Session) -> dict:
        """
        Comprehensive waste analysis
        """
        
        if not waste_logs:
            return {
                "total_waste_kg": 0,
                "top_wasted_items": [],
                "waste_by_reason": {},
                "recommendations": ["Start logging waste to get insights"]
            }
        
        # Total waste
        total_waste = sum(log.quantity_kg for log in waste_logs)
        
        # Top wasted items
        waste_by_ingredient = defaultdict(float)
        for log in waste_logs:
            ingredient = db.query(Ingredient).filter(
                Ingredient.id == log.ingredient_id
            ).first()
            if ingredient:
                waste_by_ingredient[ingredient.name] += log.quantity_kg
        
        top_wasted = sorted(
            waste_by_ingredient.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        top_wasted_items = [
            {"item": name, "total_kg": round(kg, 2)}
            for name, kg in top_wasted
        ]
        
        # Waste by reason
        waste_by_reason = defaultdict(float)
        for log in waste_logs:
            if log.reason:
                waste_by_reason[log.reason] += log.quantity_kg
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            waste_logs,
            waste_by_ingredient,
            waste_by_reason
        )
        
        return {
            "total_waste_kg": round(total_waste, 2),
            "top_wasted_items": top_wasted_items,
            "waste_by_reason": dict(waste_by_reason),
            "recommendations": recommendations
        }
    
    def _generate_recommendations(
        self,
        waste_logs: List[WasteLog],
        waste_by_ingredient: dict,
        waste_by_reason: dict
    ) -> List[str]:
        """
        Generate actionable recommendations
        """
        recommendations = []
        
        # Check for bread waste
        if any("bread" in item.lower() for item in waste_by_ingredient.keys()):
            recommendations.append(
                "Consider reducing bread quantities - it's frequently wasted"
            )
        
        # Check for flight delay issues
        if "flight delay" in waste_by_reason or "Flight delay" in waste_by_reason:
            recommendations.append(
                "Set up flight tracking alerts to adjust breakfast preparation"
            )
        
        # Check for over-preparation
        if "over-preparation" in waste_by_reason:
            recommendations.append(
                "Review portion calculations - consistent over-preparation detected"
            )
        
        # Check for weather-related waste
        if any("hot" in str(log.weather_condition).lower() for log in waste_logs if log.weather_condition):
            recommendations.append(
                "Hot weather reduces appetite - prepare 15% less on very hot days"
            )
        
        # Generic recommendation
        if len(recommendations) == 0:
            recommendations.append(
                "Continue logging waste - patterns will emerge over time"
            )
        
        # Cost savings
        avg_waste = sum(log.quantity_kg for log in waste_logs) / len(waste_logs)
        if avg_waste > 2.0:
            potential_savings = avg_waste * 30 * 5  # kg/day × days × TND/kg
            recommendations.append(
                f"Reducing daily waste by 50% could save ~{int(potential_savings)} TND/month"
            )
        
        return recommendations
    
    def get_waste_trends(self, db: Session, days: int = 30) -> dict:
        """
        Get waste trends over time
        """
        from datetime import datetime, timedelta
        
        start_date = datetime.now().date() - timedelta(days=days)
        
        waste_logs = db.query(WasteLog).filter(
            WasteLog.date >= start_date
        ).all()
        
        # Group by week
        weekly_waste = defaultdict(float)
        for log in waste_logs:
            week = log.date.isocalendar()[1]  # ISO week number
            weekly_waste[week] += log.quantity_kg
        
        return {
            "period_days": days,
            "weekly_waste": dict(weekly_waste),
            "trend": "decreasing" if self._is_decreasing(weekly_waste) else "increasing"
        }
    
    def _is_decreasing(self, weekly_data: dict) -> bool:
        """Check if waste is trending down"""
        if len(weekly_data) < 2:
            return False
        
        weeks = sorted(weekly_data.keys())
        first_half = sum(weekly_data[w] for w in weeks[:len(weeks)//2])
        second_half = sum(weekly_data[w] for w in weeks[len(weeks)//2:])
        
        return second_half < first_half