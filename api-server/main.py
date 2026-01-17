from fastapi import FastAPI, HTTPException, Depends, Query, Path
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime, timedelta
from sqlalchemy.exc import IntegrityError
from fastapi import Body
import json
from datetime import date  
# Local imports - FIXED imports
from database import get_db, engine, Base
from models import (
    Guest, Dish, Ingredient, WasteLog, Nationality, Supplier,
    Reservation, DisruptionEvent, Season
)
from schemas import *
from services.forecast import ForecastEngine
from services.cultural import CulturalEngine
from services.waste import WasteAnalyzer

# Initialize service engines (GLOBAL - outside app)
forecast_engine = ForecastEngine()
cultural_engine = CulturalEngine()
waste_analyzer = WasteAnalyzer()

# App initialization (ONLY ONCE)
app = FastAPI(title="Terroir Brain API", version="1.0.0")

# Database tables
Base.metadata.create_all(bind=engine)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# NATIONALITY ENDPOINTS
# =========================
@app.post("/nationalities/", response_model=NationalityResponse)
def create_nationality(nationality: NationalityCreate, db: Session = Depends(get_db)):
    db_nationality = Nationality(**nationality.dict())
    db.add(db_nationality)
    db.commit()
    db.refresh(db_nationality)
    return db_nationality

@app.get("/nationalities/", response_model=List[NationalityResponse])
def list_nationalities(db: Session = Depends(get_db)):
    return db.query(Nationality).all()

@app.get("/nationalities/{nationality_id}", response_model=NationalityResponse)
def get_nationality(nationality_id: int, db: Session = Depends(get_db)):
    nat = db.query(Nationality).filter(Nationality.id == nationality_id).first()
    if not nat:
        raise HTTPException(status_code=404, detail="Nationality not found")
    return nat

@app.put("/nationalities/{nationality_id}", response_model=NationalityResponse)
def update_nationality(nationality_id: int, nationality: NationalityCreate, db: Session = Depends(get_db)):
    db_nat = db.query(Nationality).filter(Nationality.id == nationality_id).first()
    if not db_nat:
        raise HTTPException(status_code=404, detail="Nationality not found")
    for key, value in nationality.dict().items():
        setattr(db_nat, key, value)
    db.commit()
    db.refresh(db_nat)
    return db_nat

@app.patch("/nationalities/{nationality_id}", response_model=NationalityResponse)
def patch_nationality(nationality_id: int, nationality: NationalityUpdate, db: Session = Depends(get_db)):
    db_nat = db.query(Nationality).filter(Nationality.id == nationality_id).first()
    if not db_nat:
        raise HTTPException(status_code=404, detail="Nationality not found")
    for key, value in nationality.dict(exclude_unset=True).items():
        setattr(db_nat, key, value)
    db.commit()
    db.refresh(db_nat)
    return db_nat

@app.delete("/nationalities/{nationality_id}")
def delete_nationality(nationality_id: int, db: Session = Depends(get_db)):
    db_nat = db.query(Nationality).filter(Nationality.id == nationality_id).first()
    if not db_nat:
        raise HTTPException(status_code=404, detail="Nationality not found")
    db.delete(db_nat)
    db.commit()
    return {"message": "Deleted successfully"}

# =========================
# GUEST ENDPOINTS
# =========================
@app.post("/guests/", response_model=GuestResponse)
def create_guest(guest: GuestCreate, db: Session = Depends(get_db)):
    nationality = db.query(Nationality).filter(Nationality.id == guest.nationality_id).first()
    if not nationality:
        raise HTTPException(status_code=400, detail=f"Nationality with id {guest.nationality_id} does not exist")
    
    existing_guest = db.query(Guest).filter(Guest.email == guest.email).first()
    if existing_guest:
        raise HTTPException(status_code=400, detail=f"Guest with email {guest.email} already exists")

    db_guest = Guest(**guest.dict())
    db.add(db_guest)
    db.commit()
    db.refresh(db_guest)
    return db_guest

@app.get("/guests/", response_model=List[GuestResponse])
def list_guests(db: Session = Depends(get_db)):
    return db.query(Guest).all()

@app.get("/guests/{guest_id}", response_model=GuestResponse)
def get_guest(guest_id: int, db: Session = Depends(get_db)):
    guest = db.query(Guest).filter(Guest.id == guest_id).first()
    if not guest:
        raise HTTPException(status_code=404, detail="Guest not found")
    return guest

@app.put("/guests/{guest_id}", response_model=GuestResponse)
def update_guest(guest_id: int, guest: GuestUpdate, db: Session = Depends(get_db)):
    db_guest = db.query(Guest).filter(Guest.id == guest_id).first()
    if not db_guest:
        raise HTTPException(status_code=404, detail="Guest not found")
    
    for key, value in guest.dict(exclude_unset=True).items():
        if key == "nationality_id":
            nationality = db.query(Nationality).filter(Nationality.id == value).first()
            if not nationality:
                raise HTTPException(status_code=400, detail=f"Nationality with id {value} does not exist")
        setattr(db_guest, key, value)
    
    db.commit()
    db.refresh(db_guest)
    return db_guest

@app.patch("/guests/{guest_id}", response_model=GuestResponse)
def patch_guest(guest_id: int, guest: GuestUpdate, db: Session = Depends(get_db)):
    db_guest = db.query(Guest).filter(Guest.id == guest_id).first()
    if not db_guest:
        raise HTTPException(status_code=404, detail="Guest not found")
    
    if hasattr(guest, 'nationality_id') and guest.nationality_id is not None:
        nationality = db.query(Nationality).filter(Nationality.id == guest.nationality_id).first()
        if not nationality:
            raise HTTPException(status_code=400, detail=f"Nationality {guest.nationality_id} does not exist")
    
    for key, value in guest.dict(exclude_unset=True).items():
        setattr(db_guest, key, value)
    
    db.commit()
    db.refresh(db_guest)
    return db_guest

@app.delete("/guests/{guest_id}")
def delete_guest(guest_id: int, db: Session = Depends(get_db)):
    db_guest = db.query(Guest).filter(Guest.id == guest_id).first()
    if not db_guest:
        raise HTTPException(status_code=404, detail="Guest not found")
    db.delete(db_guest)
    db.commit()
    return {"message": "Deleted successfully"}

# =========================
# INGREDIENT ENDPOINTS
# =========================
@app.post("/ingredients/", response_model=IngredientResponse)
def create_ingredient(ingredient: IngredientCreate, db: Session = Depends(get_db)):
    # Handle optional foreign keys
    db_ingredient = Ingredient(**ingredient.dict(exclude={"season_id", "supplier_id"}))
    if ingredient.season_id:
        db_ingredient.season_id = ingredient.season_id
    if ingredient.supplier_id:
        db_ingredient.supplier_id = ingredient.supplier_id
    db.add(db_ingredient)
    db.commit()
    db.refresh(db_ingredient)
    return db_ingredient

@app.get("/ingredients/", response_model=List[IngredientResponse])
def list_ingredients(db: Session = Depends(get_db)):
    return db.query(Ingredient).all()

@app.get("/ingredients/{ingredient_id}", response_model=IngredientResponse)
def get_ingredient(ingredient_id: int, db: Session = Depends(get_db)):
    ing = db.query(Ingredient).filter(Ingredient.id == ingredient_id).first()
    if not ing:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    return ing

@app.put("/ingredients/{ingredient_id}", response_model=IngredientResponse)
def update_ingredient(ingredient_id: int, ingredient: IngredientCreate, db: Session = Depends(get_db)):
    db_ing = db.query(Ingredient).filter(Ingredient.id == ingredient_id).first()
    if not db_ing:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    for key, value in ingredient.dict().items():
        setattr(db_ing, key, value)
    db.commit()
    db.refresh(db_ing)
    return db_ing

@app.delete("/ingredients/{ingredient_id}")
def delete_ingredient(ingredient_id: int, db: Session = Depends(get_db)):
    db_ing = db.query(Ingredient).filter(Ingredient.id == ingredient_id).first()
    if not db_ing:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    db.delete(db_ing)
    db.commit()
    return {"message": "Deleted successfully"}

@app.api_route("/ingredients/{ingredient_id}", methods=["HEAD"], response_model=None)
def head_ingredient(ingredient_id: int, db: Session = Depends(get_db)):
    ingredient = db.query(Ingredient).filter(Ingredient.id == ingredient_id).first()
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    return {}

# =========================
# DISH ENDPOINTS
# =========================
@app.post("/dishes/", response_model=DishResponse)
def create_dish(dish: DishCreate, db: Session = Depends(get_db)):
    db_dish = Dish(**dish.dict(exclude={"ingredient_ids"}))
    db.add(db_dish)
    db.commit()
    db.refresh(db_dish)
    
    if dish.ingredient_ids:
        ingredients = db.query(Ingredient).filter(Ingredient.id.in_(dish.ingredient_ids)).all()
        for ing in ingredients:
            db_dish.ingredients.append(ing)
        db.commit()
    return db_dish

@app.get("/dishes/", response_model=List[DishResponse])
def list_dishes(db: Session = Depends(get_db)):
    return db.query(Dish).all()

@app.get("/dishes/{dish_id}", response_model=DishResponse)
def get_dish(dish_id: int, db: Session = Depends(get_db)):
    dish = db.query(Dish).filter(Dish.id == dish_id).first()
    if not dish:
        raise HTTPException(status_code=404, detail="Dish not found")
    return dish

@app.put("/dishes/{dish_id}", response_model=DishResponse)
def update_dish(dish_id: int, dish: DishCreate, db: Session = Depends(get_db)):
    db_dish = db.query(Dish).filter(Dish.id == dish_id).first()
    if not db_dish:
        raise HTTPException(status_code=404, detail="Dish not found")
    
    for key, value in dish.dict(exclude={"ingredient_ids"}).items():
        setattr(db_dish, key, value)
    
    if dish.ingredient_ids:
        db_dish.ingredients = []
        ingredients = db.query(Ingredient).filter(Ingredient.id.in_(dish.ingredient_ids)).all()
        for ing in ingredients:
            db_dish.ingredients.append(ing)
    
    db.commit()
    db.refresh(db_dish)
    return db_dish

@app.patch("/dishes/{dish_id}", response_model=DishResponse)
def patch_dish(dish_id: int, dish_update: DishBase, db: Session = Depends(get_db)):
    dish = db.query(Dish).filter(Dish.id == dish_id).first()
    if not dish:
        raise HTTPException(status_code=404, detail="Dish not found")
    
    for field, value in dish_update.dict(exclude_unset=True).items():
        setattr(dish, field, value)
    
    db.commit()
    db.refresh(dish)
    return dish

@app.delete("/dishes/{dish_id}")
def delete_dish(dish_id: int, db: Session = Depends(get_db)):
    db_dish = db.query(Dish).filter(Dish.id == dish_id).first()
    if not db_dish:
        raise HTTPException(status_code=404, detail="Dish not found")
    db.delete(db_dish)
    db.commit()
    return {"message": "Deleted successfully"}

# =========================
# SUPPLIER ENDPOINTS
# =========================
@app.post("/suppliers/", response_model=SupplierResponse)
def create_supplier(supplier: SupplierCreate, db: Session = Depends(get_db)):
    db_supplier = Supplier(**supplier.dict())
    db.add(db_supplier)
    db.commit()
    db.refresh(db_supplier)
    return db_supplier

@app.get("/suppliers/", response_model=List[SupplierResponse])
def list_suppliers(db: Session = Depends(get_db)):
    return db.query(Supplier).all()

@app.get("/suppliers/{supplier_id}", response_model=SupplierResponse)
def get_supplier(supplier_id: int, db: Session = Depends(get_db)):
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return supplier

@app.put("/suppliers/{supplier_id}", response_model=SupplierResponse)
def update_supplier(supplier_id: int, supplier: SupplierCreate, db: Session = Depends(get_db)):
    db_supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not db_supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    for key, value in supplier.dict().items():
        setattr(db_supplier, key, value)
    db.commit()
    db.refresh(db_supplier)
    return db_supplier

@app.delete("/suppliers/{supplier_id}")
def delete_supplier(supplier_id: int, db: Session = Depends(get_db)):
    db_supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not db_supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    db.delete(db_supplier)
    db.commit()
    return {"message": "Deleted successfully"}

# =========================
# WASTE LOG ENDPOINTS
# =========================
@app.post("/waste-logs/", response_model=WasteLogResponse)
def create_waste_log(waste: WasteLogCreate, db: Session = Depends(get_db)):
    db_waste = WasteLog(**waste.dict())
    db.add(db_waste)
    db.commit()
    db.refresh(db_waste)
    return db_waste

@app.get("/waste-logs/", response_model=List[WasteLogResponse])
def list_waste_logs(db: Session = Depends(get_db)):
    return db.query(WasteLog).all()

@app.get("/waste-logs/{waste_id}", response_model=WasteLogResponse)
def get_waste_log(waste_id: int, db: Session = Depends(get_db)):
    wl = db.query(WasteLog).filter(WasteLog.id == waste_id).first()
    if not wl:
        raise HTTPException(status_code=404, detail="Waste log not found")
    return wl

@app.put("/waste-logs/{waste_id}", response_model=WasteLogResponse)
def update_waste_log(waste_id: int, waste: WasteLogCreate, db: Session = Depends(get_db)):
    db_waste = db.query(WasteLog).filter(WasteLog.id == waste_id).first()
    if not db_waste:
        raise HTTPException(status_code=404, detail="Waste log not found")
    for key, value in waste.dict().items():
        setattr(db_waste, key, value)
    db.commit()
    db.refresh(db_waste)
    return db_waste

@app.delete("/waste-logs/{waste_id}")
def delete_waste_log(waste_id: int, db: Session = Depends(get_db)):
    db_waste = db.query(WasteLog).filter(WasteLog.id == waste_id).first()
    if not db_waste:
        raise HTTPException(status_code=404, detail="Waste log not found")
    db.delete(db_waste)
    db.commit()
    return {"message": "Deleted successfully"}

# =========================
# DISRUPTION EVENT ENDPOINTS
# =========================
@app.post("/disruptions/", response_model=DisruptionEventResponse)
def create_disruption(event: DisruptionEventCreate, db: Session = Depends(get_db)):
    try:
        db_event = DisruptionEvent(**event.dict())
        db.add(db_event)
        db.commit()
        db.refresh(db_event)
        return db_event
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/disruptions/", response_model=List[DisruptionEventResponse])
def list_disruptions(db: Session = Depends(get_db)):
    return db.query(DisruptionEvent).all()

@app.get("/disruptions/{event_id}", response_model=DisruptionEventResponse)
def get_disruption(event_id: int, db: Session = Depends(get_db)):
    event = db.query(DisruptionEvent).filter(DisruptionEvent.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event

@app.put("/disruptions/{event_id}", response_model=DisruptionEventResponse)
def replace_disruption(event_id: int, event: DisruptionEventCreate, db: Session = Depends(get_db)):
    db_event = db.query(DisruptionEvent).filter(DisruptionEvent.id == event_id).first()
    if not db_event:
        raise HTTPException(status_code=404, detail="Event not found")
    for key, value in event.dict().items():
        setattr(db_event, key, value)
    db.commit()
    db.refresh(db_event)
    return db_event

@app.patch("/disruptions/{event_id}", response_model=DisruptionEventResponse)
def update_disruption(event_id: int, event: DisruptionEventUpdate, db: Session = Depends(get_db)):
    db_event = db.query(DisruptionEvent).filter(DisruptionEvent.id == event_id).first()
    if not db_event:
        raise HTTPException(status_code=404, detail="Event not found")
    for key, value in event.dict(exclude_unset=True).items():
        setattr(db_event, key, value)
    db.commit()
    db.refresh(db_event)
    return db_event

@app.delete("/disruptions/{event_id}")
def delete_disruption(event_id: int, db: Session = Depends(get_db)):
    db_event = db.query(DisruptionEvent).filter(DisruptionEvent.id == event_id).first()
    if not db_event:
        raise HTTPException(status_code=404, detail="Event not found")
    db.delete(db_event)
    db.commit()
    return {"message": "Deleted successfully"}

# =========================
# RESERVATION ENDPOINTS
# =========================
@app.post("/reservations/", response_model=ReservationResponse)
def create_reservation(reservation: ReservationCreate, db: Session = Depends(get_db)):
    db_reservation = Reservation(**reservation.dict())
    db.add(db_reservation)
    db.commit()
    db.refresh(db_reservation)
    return db_reservation

@app.get("/reservations/", response_model=List[ReservationResponse])
def list_reservations(db: Session = Depends(get_db)):
    return db.query(Reservation).all()

@app.get("/reservations/{reservation_id}", response_model=ReservationResponse)
def get_reservation(reservation_id: int, db: Session = Depends(get_db)):
    r = db.query(Reservation).filter(Reservation.id == reservation_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Reservation not found")
    return r

@app.put("/reservations/{reservation_id}", response_model=ReservationResponse)
def update_reservation(reservation_id: int, reservation: ReservationCreate, db: Session = Depends(get_db)):
    db_reservation = db.query(Reservation).filter(Reservation.id == reservation_id).first()
    if not db_reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")
    for key, value in reservation.dict().items():
        setattr(db_reservation, key, value)
    db.commit()
    db.refresh(db_reservation)
    return db_reservation

@app.patch("/reservations/{reservation_id}", response_model=ReservationResponse)
def patch_reservation(reservation_id: int, reservation: ReservationBase, db: Session = Depends(get_db)):
    db_reservation = db.query(Reservation).filter(Reservation.id == reservation_id).first()
    if not db_reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")
    for key, value in reservation.dict(exclude_unset=True).items():
        setattr(db_reservation, key, value)
    db.commit()
    db.refresh(db_reservation)
    return db_reservation

@app.delete("/reservations/{reservation_id}")
def delete_reservation(reservation_id: int, db: Session = Depends(get_db)):
    db_reservation = db.query(Reservation).filter(Reservation.id == reservation_id).first()
    if not db_reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")
    db.delete(db_reservation)
    db.commit()
    return {"message": "Deleted successfully"}

# =========================
# ADVANCED INTELLIGENCE ENDPOINTS
# =========================

from collections import defaultdict
from datetime import timedelta

# =========================
# 1. SMART PROCUREMENT OPTIMIZER
# =========================
@app.post("/intelligence/procurement-optimizer")
def procurement_optimizer(
    start_date: str = Query(..., description="Start date YYYY-MM-DD"),
    end_date: str = Query(..., description="End date YYYY-MM-DD"),
    guest_profile: dict = Body(..., description="Guest profile with nationalities and counts"),
    db: Session = Depends(get_db)
):
    """
    🎯 ADVANCED: Generate optimized shopping list for a date range
    
    Features:
    - Multi-day forecasting
    - Bulk discount detection (>10kg gets 10% off)
    - Local vs imported cost comparison
    - Carbon footprint calculation
    - Waste risk assessment
    - Alternative ingredient suggestions
    
    Request Body Example:
    {
        "guests": [
            {"nationality": "FRA", "count": 10, "dates": ["2025-01-10", "2025-01-11"]},
            {"nationality": "DEU", "count": 5, "dates": ["2025-01-10"]}
        ]
    }
    """
    try:
        start = date.fromisoformat(start_date)
        end = date.fromisoformat(end_date)
        
        # Aggregate demand across all dates and nationalities
        total_demand = defaultdict(float)
        ingredient_details = {}
        
        for guest_group in guest_profile.get("guests", []):
            nationality_code = guest_group["nationality"]
            count = guest_group["count"]
            dates = [date.fromisoformat(d) for d in guest_group["dates"]]
            
            # Get nationality
            nat = db.query(Nationality).filter(
                Nationality.code == nationality_code.upper()
            ).first()
            if not nat:
                continue
            
            # Calculate demand for each date
            for target_date in dates:
                ingredients = db.query(Ingredient).all()
                for ing in ingredients:
                    demand = forecast_engine.calculate_demand(
                        ingredient=ing,
                        occupancy=count,
                        nationality=nat,
                        date=target_date,
                        db=db
                    )
                    total_demand[ing.id] += demand
                    ingredient_details[ing.id] = ing
        
        # Build optimized shopping list
        shopping_list = []
        total_cost = 0
        total_carbon = 0
        
        for ing_id, quantity in total_demand.items():
            ing = ingredient_details[ing_id]
            
            # Calculate costs
            base_cost = quantity * ing.cost_per_unit
            
            # Bulk discount (>10kg gets 10% off)
            if quantity > 10:
                final_cost = base_cost * 0.9
                discount = base_cost * 0.1
            else:
                final_cost = base_cost
                discount = 0
            
            # Carbon footprint (distance-based)
            if ing.supplier and ing.supplier.distance_km:
                carbon_kg = quantity * ing.supplier.distance_km * 0.05  # 0.05 kg CO2 per km
            else:
                carbon_kg = 0
            
            # Waste risk (check historical waste)
            recent_waste = db.query(WasteLog).filter(
                WasteLog.ingredient_id == ing_id
            ).order_by(WasteLog.date.desc()).limit(5).all()
            
            avg_waste_rate = 0
            if recent_waste:
                avg_waste = sum(log.quantity_kg for log in recent_waste) / len(recent_waste)
                avg_waste_rate = (avg_waste / ing.base_consumption_rate) if ing.base_consumption_rate > 0 else 0
            
            waste_risk = "HIGH" if avg_waste_rate > 0.3 else "MEDIUM" if avg_waste_rate > 0.15 else "LOW"
            
            # Suggested order quantity (reduce if high waste risk)
            if waste_risk == "HIGH":
                suggested_quantity = quantity * 0.85
                adjustment_note = "Reduced by 15% due to high waste history"
            elif waste_risk == "MEDIUM":
                suggested_quantity = quantity * 0.92
                adjustment_note = "Reduced by 8% due to moderate waste history"
            else:
                suggested_quantity = quantity
                adjustment_note = "No adjustment needed"
            
            total_cost += final_cost
            total_carbon += carbon_kg
            
            shopping_list.append({
                "ingredient_id": ing.id,
                "name": ing.name,
                "name_ar": ing.name_ar,
                "forecasted_need": round(quantity, 2),
                "suggested_order": round(suggested_quantity, 2),
                "unit": ing.unit,
                "supplier": ing.supplier.name if ing.supplier else "No supplier",
                "distance_km": ing.supplier.distance_km if ing.supplier else None,
                "base_cost_tnd": round(base_cost, 2),
                "discount_tnd": round(discount, 2),
                "final_cost_tnd": round(final_cost, 2),
                "carbon_footprint_kg": round(carbon_kg, 2),
                "waste_risk": waste_risk,
                "adjustment_note": adjustment_note,
                "is_local": ing.supplier.distance_km < 20 if ing.supplier and ing.supplier.distance_km else False
            })
        
        # Sort by cost (highest first)
        shopping_list.sort(key=lambda x: x["final_cost_tnd"], reverse=True)
        
        # Generate optimization insights
        local_items = [item for item in shopping_list if item["is_local"]]
        high_risk_items = [item for item in shopping_list if item["waste_risk"] == "HIGH"]
        
        insights = {
            "total_items": len(shopping_list),
            "total_cost_tnd": round(total_cost, 2),
            "total_carbon_kg": round(total_carbon, 2),
            "local_sourcing_percentage": round(len(local_items) / len(shopping_list) * 100, 1) if shopping_list else 0,
            "bulk_discount_savings_tnd": round(sum(item["discount_tnd"] for item in shopping_list), 2),
            "high_risk_items_count": len(high_risk_items),
            "recommendations": []
        }
        
        # Smart recommendations
        if insights["local_sourcing_percentage"] < 50:
            insights["recommendations"].append("Consider switching to more local suppliers to reduce carbon footprint")
        
        if len(high_risk_items) > 0:
            insights["recommendations"].append(f"{len(high_risk_items)} items have high waste risk - consider smaller initial orders")
        
        if insights["total_carbon_kg"] > 100:
            insights["recommendations"].append("High carbon footprint detected - prioritize local ingredients")
        
        return {
            "period": {"start": start_date, "end": end_date},
            "shopping_list": shopping_list,
            "insights": insights
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =========================
# 2. NATIONALITY COMPARISON ANALYZER
# =========================
@app.get("/intelligence/nationality-comparison")
def nationality_comparison(
    occupancy: int = Query(10, description="Number of guests"),
    db: Session = Depends(get_db)
):
    """
    🎯 ADVANCED: Compare ingredient demand across ALL nationalities
    
    Shows:
    - Which nationalities consume most/least of each ingredient
    - Cost differences between serving different nationalities
    - Cultural preference patterns
    - Budget planning for mixed groups
    
    Use case: "We have 10 French guests next week and 10 German guests the week after.
               How will costs differ?"
    """
    try:
        nationalities = db.query(Nationality).all()
        ingredients = db.query(Ingredient).all()
        
        comparison_matrix = []
        
        for ing in ingredients:
            ing_comparison = {
                "ingredient_id": ing.id,
                "ingredient_name": ing.name,
                "unit": ing.unit,
                "base_rate": ing.base_consumption_rate,
                "by_nationality": []
            }
            
            demands = []
            for nat in nationalities:
                demand = forecast_engine.calculate_demand(
                    ingredient=ing,
                    occupancy=occupancy,
                    nationality=nat,
                    date=date.today(),
                    db=db
                )
                cost = demand * ing.cost_per_unit
                
                demands.append({
                    "nationality": nat.name,
                    "code": nat.code,
                    "demand_kg": round(demand, 2),
                    "cost_tnd": round(cost, 2),
                    "multiplier": round(demand / (occupancy * ing.base_consumption_rate), 2) if ing.base_consumption_rate > 0 else 1.0
                })
            
            # Sort by demand
            demands.sort(key=lambda x: x["demand_kg"], reverse=True)
            
            ing_comparison["by_nationality"] = demands
            ing_comparison["highest_consumer"] = demands[0]["nationality"]
            ing_comparison["lowest_consumer"] = demands[-1]["nationality"]
            ing_comparison["variance_percentage"] = round(
                ((demands[0]["demand_kg"] - demands[-1]["demand_kg"]) / demands[-1]["demand_kg"] * 100) 
                if demands[-1]["demand_kg"] > 0 else 0, 
                1
            )
            
            comparison_matrix.append(ing_comparison)
        
        # Generate insights
        bread_items = [item for item in comparison_matrix if "bread" in item["ingredient_name"].lower()]
        dairy_items = [item for item in comparison_matrix if any(x in item["ingredient_name"].lower() for x in ["yogurt", "cheese", "milk"])]
        
        insights = {
            "highest_variance_ingredient": max(comparison_matrix, key=lambda x: x["variance_percentage"]),
            "bread_insights": {
                "highest_consumer": max(bread_items, key=lambda x: x["by_nationality"][0]["demand_kg"])["by_nationality"][0]["nationality"] if bread_items else None,
                "average_variance": round(sum(item["variance_percentage"] for item in bread_items) / len(bread_items), 1) if bread_items else 0
            },
            "dairy_insights": {
                "highest_consumer": max(dairy_items, key=lambda x: x["by_nationality"][0]["demand_kg"])["by_nationality"][0]["nationality"] if dairy_items else None,
                "average_variance": round(sum(item["variance_percentage"] for item in dairy_items) / len(dairy_items), 1) if dairy_items else 0
            }
        }
        
        return {
            "comparison_matrix": comparison_matrix,
            "insights": insights
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =========================
# 3. WASTE IMPACT SIMULATOR
# =========================
@app.post("/intelligence/waste-impact-simulator")
def waste_impact_simulator(
    scenario: dict = Body(..., description="What-if scenario"),
    db: Session = Depends(get_db)
):
    """
    🎯 ADVANCED: Simulate impact of waste reduction strategies
    
    Scenarios:
    - "What if we reduce bread orders by 20%?"
    - "What if we implement flight tracking?"
    - "What if we adjust for weather forecasts?"
    
    Request Body Example:
    {
        "strategy": "reduce_bread_by_percentage",
        "parameters": {"percentage": 20},
        "time_horizon_days": 30
    }
    
    OR
    
    {
        "strategy": "implement_flight_tracking",
        "parameters": {"estimated_delay_reduction": 0.6},
        "time_horizon_days": 30
    }
    """
    try:
        strategy = scenario.get("strategy")
        params = scenario.get("parameters", {})
        days = scenario.get("time_horizon_days", 30)
        
        # Get current waste baseline
        from_date = date.today() - timedelta(days=days)
        current_waste = db.query(WasteLog).filter(WasteLog.date >= from_date).all()
        
        current_total_waste = sum(log.quantity_kg for log in current_waste)
        current_cost = sum(
            log.quantity_kg * db.query(Ingredient).get(log.ingredient_id).cost_per_unit
            for log in current_waste
        )
        
        # Simulate different strategies
        projected_waste = current_total_waste
        projected_cost = current_cost
        
        if strategy == "reduce_bread_by_percentage":
            percentage = params.get("percentage", 20) / 100
            bread_waste = sum(
                log.quantity_kg for log in current_waste 
                if "bread" in db.query(Ingredient).get(log.ingredient_id).name.lower()
            )
            bread_reduction = bread_waste * percentage
            projected_waste -= bread_reduction
            
            bread_cost = sum(
                log.quantity_kg * db.query(Ingredient).get(log.ingredient_id).cost_per_unit
                for log in current_waste
                if "bread" in db.query(Ingredient).get(log.ingredient_id).name.lower()
            )
            projected_cost -= (bread_cost * percentage)
            
        elif strategy == "implement_flight_tracking":
            delay_reduction = params.get("estimated_delay_reduction", 0.6)
            delay_waste = sum(
                log.quantity_kg for log in current_waste
                if log.reason and "flight" in log.reason.lower()
            )
            waste_reduction = delay_waste * delay_reduction
            projected_waste -= waste_reduction
            
            delay_cost = sum(
                log.quantity_kg * db.query(Ingredient).get(log.ingredient_id).cost_per_unit
                for log in current_waste
                if log.reason and "flight" in log.reason.lower()
            )
            projected_cost -= (delay_cost * delay_reduction)
            
        elif strategy == "weather_adjustment":
            adjustment_factor = params.get("adjustment_factor", 0.15)
            hot_weather_waste = sum(
                log.quantity_kg for log in current_waste
                if log.weather_condition and "hot" in log.weather_condition.lower()
            )
            waste_reduction = hot_weather_waste * adjustment_factor
            projected_waste -= waste_reduction
            
            hot_cost = sum(
                log.quantity_kg * db.query(Ingredient).get(log.ingredient_id).cost_per_unit
                for log in current_waste
                if log.weather_condition and "hot" in log.weather_condition.lower()
            )
            projected_cost -= (hot_cost * adjustment_factor)
        
        # Calculate impact
        waste_reduction = current_total_waste - projected_waste
        cost_savings = current_cost - projected_cost
        
        # Extrapolate to yearly
        yearly_savings = (cost_savings / days) * 365
        
        return {
            "strategy": strategy,
            "parameters": params,
            "time_horizon_days": days,
            "current_state": {
                "total_waste_kg": round(current_total_waste, 2),
                "total_cost_tnd": round(current_cost, 2)
            },
            "projected_state": {
                "total_waste_kg": round(projected_waste, 2),
                "total_cost_tnd": round(projected_cost, 2)
            },
            "impact": {
                "waste_reduction_kg": round(waste_reduction, 2),
                "waste_reduction_percentage": round((waste_reduction / current_total_waste * 100) if current_total_waste > 0 else 0, 1),
                "cost_savings_tnd": round(cost_savings, 2),
                "monthly_savings_tnd": round((cost_savings / days) * 30, 2),
                "yearly_savings_tnd": round(yearly_savings, 2)
            },
            "recommendation": "Implement this strategy" if cost_savings > 100 else "Impact is minimal, consider other strategies"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =========================
# 4. REAL-TIME KITCHEN DASHBOARD
# =========================
@app.get("/intelligence/kitchen-dashboard")
def kitchen_dashboard(db: Session = Depends(get_db)):
    """
    🎯 ADVANCED: Real-time decision support for kitchen managers
    
    Provides:
    - Today's prep requirements
    - Upcoming reservations impact
    - Urgent alerts (low stock, high waste items)
    - Weather-adjusted recommendations
    - Cost efficiency score
    """
    try:
        today = date.today()
        tomorrow = today + timedelta(days=1)
        
        # Today's reservations
        today_reservations = db.query(Reservation).filter(Reservation.date == today).all()
        tomorrow_reservations = db.query(Reservation).filter(Reservation.date == tomorrow).all()
        
        today_occupancy = len(today_reservations)
        tomorrow_occupancy = len(tomorrow_reservations)
        
        # Get nationality breakdown for today
        nationality_breakdown = defaultdict(int)
        for res in today_reservations:
            guest = db.query(Guest).get(res.guest_id)
            if guest:
                nat = db.query(Nationality).get(guest.nationality_id)
                if nat:
                    nationality_breakdown[nat.code] += 1
        
        # Today's ingredient needs
        ingredients = db.query(Ingredient).all()
        prep_list = []
        
        for ing in ingredients:
            total_demand = 0
            for nat_code, count in nationality_breakdown.items():
                nat = db.query(Nationality).filter(Nationality.code == nat_code).first()
                if nat:
                    demand = forecast_engine.calculate_demand(
                        ingredient=ing,
                        occupancy=count,
                        nationality=nat,
                        date=today,
                        db=db
                    )
                    total_demand += demand
            
            if total_demand > 0:
                prep_list.append({
                    "ingredient": ing.name,
                    "quantity": round(total_demand, 2),
                    "unit": ing.unit,
                    "priority": "HIGH" if ing.is_staple else "NORMAL"
                })
        
        # Alerts
        alerts = []
        
        # Check for disruptions today
        disruptions = db.query(DisruptionEvent).filter(
            DisruptionEvent.occurred_at == today
        ).all()
        
        if disruptions:
            for dis in disruptions:
                alerts.append({
                    "type": "DISRUPTION",
                    "severity": "HIGH",
                    "message": f"{dis.title}: Reduce all prep by {int((1-dis.severity)*100)}%",
                    "action": f"Adjust quantities down by {int((1-dis.severity)*100)}%"
                })
        
        # Check recent high waste items
        recent_waste = db.query(WasteLog).filter(
            WasteLog.date >= today - timedelta(days=7)
        ).all()
        
        waste_by_ingredient = defaultdict(float)
        for log in recent_waste:
            waste_by_ingredient[log.ingredient_id] += log.quantity_kg
        
        for ing_id, waste_amount in waste_by_ingredient.items():
            if waste_amount > 2.0:  # More than 2kg wasted in last week
                ing = db.query(Ingredient).get(ing_id)
                alerts.append({
                    "type": "WASTE_ALERT",
                    "severity": "MEDIUM",
                    "message": f"{ing.name} has {round(waste_amount, 1)}kg waste in last 7 days",
                    "action": f"Reduce {ing.name} prep by 15-20%"
                })
        
        # Tomorrow's forecast
        tomorrow_prep = []
        if tomorrow_occupancy > 0:
            for ing in ingredients[:5]:  # Top 5 ingredients
                # Use most common nationality or default
                main_nat = db.query(Nationality).filter(Nationality.code == "FRA").first()
                demand = forecast_engine.calculate_demand(
                    ingredient=ing,
                    occupancy=tomorrow_occupancy,
                    nationality=main_nat,
                    date=tomorrow,
                    db=db
                )
                if demand > 0:
                    tomorrow_prep.append({
                        "ingredient": ing.name,
                        "quantity": round(demand, 2),
                        "unit": ing.unit
                    })
        
        return {
            "date": str(today),
            "occupancy": {
                "today": today_occupancy,
                "tomorrow": tomorrow_occupancy,
                "today_breakdown": dict(nationality_breakdown)
            },
            "prep_requirements": sorted(prep_list, key=lambda x: x["priority"] == "HIGH", reverse=True),
            "alerts": alerts,
            "tomorrow_forecast": tomorrow_prep,
            "status": "NORMAL" if len(alerts) == 0 else "ATTENTION_NEEDED"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =========================
# 5. SEASONAL MENU OPTIMIZER
# =========================
@app.get("/intelligence/seasonal-optimizer")
def seasonal_optimizer(
    month: int = Query(..., ge=1, le=12, description="Target month"),
    db: Session = Depends(get_db)
):
    """
    🎯 ADVANCED: Optimize menu for maximum seasonality and sustainability
    
    Provides:
    - Best dishes for the month (highest seasonal score)
    - Carbon footprint by dish
    - Cost efficiency analysis
    - Alternative suggestions for out-of-season items
    - Traditional vs modern balance
    """
    try:
        # Get all seasons and find current
        all_seasons = db.query(Season).all()
        current_season = None
        
        for s in all_seasons:
            try:
                months_list = json.loads(s.months) if isinstance(s.months, str) else s.months
                if month in months_list:
                    current_season = s
                    break
            except:
                continue
        
        # Get all dishes
        dishes = db.query(Dish).all()
        
        dish_analysis = []
        
        for dish in dishes:
            # Calculate seasonality score
            seasonal_ingredients = 0
            total_ingredients = len(dish.ingredients)
            
            if total_ingredients == 0:
                continue
            
            for ing in dish.ingredients:
                if ing.season_id == current_season.id if current_season else False:
                    seasonal_ingredients += 1
            
            seasonality_score = (seasonal_ingredients / total_ingredients) * 100 if total_ingredients > 0 else 0
            
            # Calculate carbon footprint
            carbon = sum(
                (ing.supplier.distance_km * 0.5) if ing.supplier and ing.supplier.distance_km else 0
                for ing in dish.ingredients
            )
            
            # Calculate cost
            cost = sum(
                ing.cost_per_unit * ing.base_consumption_rate
                for ing in dish.ingredients
            )
            
            # Local sourcing
            local_count = sum(
                1 for ing in dish.ingredients
                if ing.supplier and ing.supplier.distance_km and ing.supplier.distance_km < 20
            )
            
            local_percentage = (local_count / total_ingredients) * 100 if total_ingredients > 0 else 0
            
            dish_analysis.append({
                "dish_id": dish.id,
                "dish_name": dish.name,
                "is_traditional": dish.is_traditional,
                "seasonality_score": round(seasonality_score, 1),
                "carbon_footprint": round(carbon, 2),
                "estimated_cost_per_serving": round(cost, 2),
                "local_sourcing_percentage": round(local_percentage, 1),
                "sustainability_grade": (
                    "A" if seasonality_score > 70 and local_percentage > 70
                    else "B" if seasonality_score > 50
                    else "C"
                ),
                "ingredients": [ing.name for ing in dish.ingredients]
            })
        
        # Sort by seasonality score
        dish_analysis.sort(key=lambda x: x["seasonality_score"], reverse=True)
        
        # Generate recommendations
        top_dishes = dish_analysis[:3]
        traditional_dishes = [d for d in dish_analysis if d["is_traditional"]]
        
        recommendations = {
            "recommended_dishes": [d["dish_name"] for d in top_dishes],
            "most_sustainable": max(dish_analysis, key=lambda x: x["sustainability_grade"] == "A")["dish_name"] if dish_analysis else None,
            "traditional_options": [d["dish_name"] for d in traditional_dishes[:3]],
            "cost_range": {
                "lowest": min(d["estimated_cost_per_serving"] for d in dish_analysis) if dish_analysis else 0,
                "highest": max(d["estimated_cost_per_serving"] for d in dish_analysis) if dish_analysis else 0
            }
        }
        
        return {
            "month": month,
            "season": current_season.name if current_season else "Unknown",
            "dish_analysis": dish_analysis,
            "recommendations": recommendations
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =========================
# 6. COST-BENEFIT ANALYZER
# =========================
@app.get("/intelligence/cost-benefit-analysis")
def cost_benefit_analyzer(
    days: int = Query(30, description="Analysis period"),
    db: Session = Depends(get_db)
):
    """
    🎯 ADVANCED: Comprehensive financial impact analysis
    
    Shows:
    - ROI of using the Terroir Brain system
    - Actual savings vs baseline
    - Efficiency metrics
    - Cost per guest trends
    - Break-even analysis
    """
    try:
        from_date = date.today() - timedelta(days=days)
        
        # Get waste logs
        waste_logs = db.query(WasteLog).filter(WasteLog.date >= from_date).all()
        
        # Calculate waste cost
        waste_cost = sum(
            log.quantity_kg * db.query(Ingredient).get(log.ingredient_id).cost_per_unit
            for log in waste_logs
        )
        
        # Get reservations to calculate occupancy
        reservations = db.query(Reservation).filter(Reservation.date >= from_date).all()
        total_guest_days = len(reservations)
        
        # Calculate metrics
        waste_per_guest = waste_cost / total_guest_days if total_guest_days > 0 else 0
        
        # Estimated baseline (before Terroir Brain) - assume 40% more waste
        estimated_baseline_waste = waste_cost * 1.4
        actual_savings = estimated_baseline_waste - waste_cost
        
        # Project yearly
        daily_savings = actual_savings / days
        monthly_savings = daily_savings * 30
        yearly_savings = daily_savings * 365
        
        # Calculate efficiency score
        waste_percentage = (waste_cost / (waste_cost + 1000)) * 100  # Assuming 1000 TND is normal food cost
        efficiency_score = max(0, 100 - waste_percentage)
        
        return {
            "period_days": days,
            "waste_analysis": {
                "total_waste_cost_tnd": round(waste_cost, 2),
                "waste_per_guest_tnd": round(waste_per_guest, 2),
                "estimated_baseline_waste_tnd": round(estimated_baseline_waste, 2)
            },
            "savings": {
                "actual_savings_tnd": round(actual_savings, 2),
                "monthly_savings_tnd": round(monthly_savings, 2),
                "yearly_projection_tnd": round(yearly_savings, 2),
                "roi_percentage": round((actual_savings / 1000) * 100, 1) if waste_cost > 0 else 0
            },
            "efficiency": {
                "efficiency_score": round(efficiency_score, 1),
                "grade": "A" if efficiency_score > 90 else "B" if efficiency_score > 75 else "C",
                "total_guest_days": total_guest_days
            },
            "recommendation": (
                "Excellent performance! System is delivering strong ROI" if efficiency_score > 85
                else "Good performance, continue monitoring waste patterns" if efficiency_score > 70
                else "Improvement needed - review waste logs and adjust forecasts"
            )
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =========================
# 7. CULTURAL INSIGHTS DEEP DIVE
# =========================
@app.get("/intelligence/cultural-insights")
def cultural_insights_analyzer(db: Session = Depends(get_db)):
    """
    🎯 ADVANCED: Deep cultural preference analysis

    Shows:
    - Preference heatmap across nationalities
    - Most/least compatible guest combinations
    - Menu diversity requirements
    - Cultural accommodation score
    - Best ingredient investments per nationality
    """
    try:
        nationalities = db.query(Nationality).all()
        ingredients = db.query(Ingredient).all()

        # Build preference matrix
        preference_matrix = {}

        for nat in nationalities:
            nat_preferences = {
                "code": nat.code,
                "name": nat.name,
                "preferences": {
                    "bread": nat.bread_preference,
                    "dairy": nat.dairy_preference,
                    "spice": nat.spice_tolerance
                },
                "breakfast_style": nat.breakfast_style,
                "high_demand_ingredients": [],
                "low_demand_ingredients": []
            }

            # Calculate demand for key ingredients
            for ing in ingredients:
                demand = forecast_engine.calculate_demand(
                    ingredient=ing,
                    occupancy=10,
                    nationality=nat ,
                    date=date.today(),  # ← new argument
                    db=db 
                )
                if demand > 2.0:
                    nat_preferences["high_demand_ingredients"].append(ing.name)
                elif demand < 0.5:
                    nat_preferences["low_demand_ingredients"].append(ing.name)

            preference_matrix[nat.code] = nat_preferences

        # Find nationality compatibility
        compatibility = []
        nat_list = list(nationalities)

        for i in range(len(nat_list)):
            for j in range(i + 1, len(nat_list)):
                nat1 = nat_list[i]
                nat2 = nat_list[j]

                # Calculate compatibility score
                bread_diff = abs(nat1.bread_preference - nat2.bread_preference)
                dairy_diff = abs(nat1.dairy_preference - nat2.dairy_preference)
                spice_diff = abs(nat1.spice_tolerance - nat2.spice_tolerance)

                compatibility_score = 100 - ((bread_diff + dairy_diff + spice_diff) / 3 * 50)

                compatibility.append({
                    "pair": f"{nat1.name} + {nat2.name}",
                    "codes": f"{nat1.code}-{nat2.code}",
                    "compatibility_score": round(compatibility_score, 1),
                    "status": "HIGH" if compatibility_score > 80 else "MEDIUM" if compatibility_score > 60 else "LOW",
                    "note": (
                        "Similar preferences, easy to accommodate" if compatibility_score > 80
                        else "Moderate differences, manageable with variety" if compatibility_score > 60
                        else "Significant differences, requires diverse menu"
                    )
                })

        compatibility.sort(key=lambda x: x["compatibility_score"], reverse=True)

        # Generate insights
        most_compatible = compatibility[0] if compatibility else None
        least_compatible = compatibility[-1] if compatibility else None

        # Find most demanding nationality (highest overall preferences)
        most_demanding = max(
            nationalities,
            key=lambda n: n.bread_preference + n.dairy_preference + n.spice_tolerance
        )

        # Find least demanding (closest to neutral 1.0)
        least_demanding = min(
            nationalities,
            key=lambda n: abs(n.bread_preference - 1.0) + abs(n.dairy_preference - 1.0) + abs(n.spice_tolerance - 1.0)
        )

        return {
            "preference_matrix": preference_matrix,
            "compatibility_analysis": compatibility,
            "insights": {
                "most_compatible_pair": most_compatible,
                "least_compatible_pair": least_compatible,
                "most_demanding_nationality": {
                    "name": most_demanding.name,
                    "total_preference_score": round(
                        most_demanding.bread_preference + most_demanding.dairy_preference + most_demanding.spice_tolerance,
                        2
                    )
                },
                "least_demanding_nationality": {
                    "name": least_demanding.name,
                    "note": "Closest to neutral preferences, easiest to accommodate"
                },
                "diversity_requirement": "HIGH" if least_compatible and least_compatible["compatibility_score"] < 60 else "MEDIUM"
            },
            "recommendations": [
                f"When hosting {most_compatible['pair']}, you can use a simpler menu" if most_compatible else "",
                f"When hosting {least_compatible['pair']}, prepare diverse options" if least_compatible else "",
                f"{most_demanding.name} guests require {int((most_demanding.bread_preference - 1.0) * 100)}% more bread than average"
            ]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
import requests # You'll need to install this

@app.get("/intelligence/global-mashup")
def global_intelligence_mashup(db: Session = Depends(get_db)):
    """
    🌍 THE GLOBAL MASHUP:
    Combines: Local Guest Data + Real-time Weather + Exchange Rates
    """
    # 1. Internal Data: Get today's occupancy
    today = date.today()
    guests = db.query(Reservation).filter(Reservation.date == today).count()
    
    # 2. External Data: Weather in Tunis (using a free API like Open-Meteo)
    # This helps decide if you should prep 'Couscous' (cold) or 'Salade Méchouia' (hot)
    weather_res = requests.get("https://api.open-meteo.com/v1/forecast?latitude=36.8&longitude=10.1&current_weather=true")
    temp = weather_res.json().get("current_weather", {}).get("temperature")
    
    # 3. External Data: Currency Exchange (TND to EUR)
    # Useful for showing your European guests the cost of their meals in their own currency
    currency_res = requests.get("https://api.exchangerate-api.com/v4/latest/TND")
    tnd_to_eur = currency_res.json().get("rates", {}).get("EUR")

    # 4. Logic Mashup
    recommendation = "Suggest indoor dining" if temp < 15 else "Prepare the terrace"
    
    return {
        "local_context": {
            "guests_arriving": guests,
            "date": today
        },
        "external_factors": {
            "tunis_temperature": f"{temp}°C",
            "exchange_rate": f"1 TND = {tnd_to_eur} EUR"
        },
        "ai_suggestion": {
            "action": recommendation,
            "menu_tweak": "Hot mint tea" if temp < 18 else "Fresh Citronnade"
        }
    }