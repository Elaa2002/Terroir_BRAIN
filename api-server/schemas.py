"""
Pydantic schemas for API requests and responses
"""

from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import date, datetime


# ==========================
# NATIONALITY SCHEMAS
# ==========================

class NationalityUpdate(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None
    bread_preference: Optional[float] = None
    dairy_preference: Optional[float] = None
    spice_tolerance: Optional[float] = None
    breakfast_style: Optional[str] = None

# ==========================
# GUEST UPDATE SCHEMA
# ==========================

class GuestUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    nationality_id: Optional[int] = None
    dietary_restrictions: Optional[str] = None

class NationalityBase(BaseModel):
    code: str
    name: str
    bread_preference: float = 1.0
    dairy_preference: float = 1.0
    spice_tolerance: float = 1.0
    breakfast_style: Optional[str] = None

class NationalityCreate(NationalityBase):
    pass

class NationalityResponse(NationalityBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# ==========================
# GUEST SCHEMAS
# ==========================

class GuestBase(BaseModel):
    name: str
    email: EmailStr
    nationality_id: int
    dietary_restrictions: Optional[str] = None

class GuestCreate(GuestBase):
    pass

class GuestResponse(GuestBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
class GuestUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    nationality_id: Optional[int] = None
    dietary_restrictions: Optional[str] = None
# ==========================
# INGREDIENT SCHEMAS
# ==========================

class IngredientBase(BaseModel):
    name: str
    name_ar: Optional[str] = None
    base_consumption_rate: float = 1.0
    unit: str = "kg"
    cost_per_unit: float = 0.0
    is_traditional: bool = False
    is_staple: bool = False

class IngredientCreate(IngredientBase):
    season_id: Optional[int] = None
    supplier_id: Optional[int] = None

class IngredientResponse(IngredientBase):
    id: int
    season_id: Optional[int]
    supplier_id: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True

# ==========================
# DISH SCHEMAS
# ==========================

class DishBase(BaseModel):
    name: str
    name_ar: Optional[str] = None
    description: Optional[str] = None
    is_traditional: bool = False
    cuisine_type: Optional[str] = None
    meal_type: Optional[str] = None

class DishCreate(DishBase):
    ingredient_ids: Optional[List[int]] = []

class DishResponse(DishBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# ==========================
# WASTE LOG SCHEMAS
# ==========================

class WasteLogBase(BaseModel):
    ingredient_id: int
    quantity_kg: float
    date: date
    reason: Optional[str] = None
    occupancy_on_date: Optional[int] = None
    weather_condition: Optional[str] = None

class WasteLogCreate(WasteLogBase):
    pass

class WasteLogResponse(WasteLogBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# ==========================
# FORECAST SCHEMAS
# ==========================

class IngredientForecast(BaseModel):
    ingredient_id: int
    ingredient_name: str
    quantity: float
    unit: str
    seasonality_score: float

class ForecastResponse(BaseModel):
    date: date
    occupancy: int
    nationality: str
    ingredients: List[IngredientForecast]

# ==========================
# WASTE ANALYSIS SCHEMAS
# ==========================

class WasteAnalysisResponse(BaseModel):
    total_waste_kg: float
    top_wasted_items: List[dict]
    waste_by_reason: dict
    recommendations: List[str]

# ==========================
# MENU SCHEMAS
# ==========================


from pydantic import BaseModel
from typing import List, Optional

class MenuDish(BaseModel):
    dish_id: int
    dish_name: str
    is_traditional: bool
    seasonality_score: float
    ingredients: List[str]
    justification: List[str]

class MenuResponse(BaseModel):
    month: int
    nationality: Optional[str]
    dishes: List[MenuDish]
    cultural_notes: str

class MenuJustification(BaseModel):
    dish_name: str
    reasons: List[str]

# ==========================
# SUPPLIER SCHEMAS
# ==========================

class SupplierBase(BaseModel):
    name: str
    location: Optional[str] = None
    distance_km: Optional[float] = None
    contact_phone: Optional[str] = None
    specialization: Optional[str] = None

class SupplierCreate(SupplierBase):
    pass
class SupplierUpdate(SupplierBase):
    pass  
class SupplierResponse(SupplierBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ==========================
# SEASON SCHEMAS
# ==========================

class SeasonBase(BaseModel):
    name: str
    months: str  # JSON string like "[1,2,3]"
    score: float = 1.0
    description: Optional[str] = None

class SeasonCreate(SeasonBase):
    pass

class SeasonResponse(SeasonBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# ==========================
# DISRUPTION EVENT SCHEMAS
# ==========================

class DisruptionEventBase(BaseModel):
    title: str
    severity: float
    occurred_at: datetime
    event_type: str
    description: str


class DisruptionEventCreate(DisruptionEventBase):
    pass


class DisruptionEventUpdate(BaseModel):
    title: Optional[str] = None
    severity: Optional[float] = None
    occurred_at: Optional[datetime] = None
    event_type: Optional[str] = None
    description: Optional[str] = None


class DisruptionEventResponse(DisruptionEventBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# ==========================
# RESERVATION SCHEMAS
# ==========================

class ReservationBase(BaseModel):
    guest_id: int
    dish_id: int
    date: date
    quantity: int = 1
    notes: Optional[str] = None

class ReservationCreate(ReservationBase):
    pass

class ReservationResponse(ReservationBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True



class ForecastResponse(BaseModel):
    ingredient_id: int
    name: str
    demand_kg: float

class ExplainForecastResponse(BaseModel):
    ingredient_name: str
    demand_kg: float
    explanation: str



class WasteAnalysisResponse(BaseModel):
    total_waste_kg: float
    top_wasted_items: List[dict]
    waste_by_reason: dict
    recommendations: List[str]




# Explain Forecast Schema
class ExplainForecastResponse(BaseModel):
    ingredient_name: str
    demand_kg: float
    explanation: str






# Waste Analysis Schema
class WasteAnalysisResponse(BaseModel):
    total_waste_kg: float
    top_wasted_items: List[dict]
    waste_by_reason: dict
    recommendations: List[str]