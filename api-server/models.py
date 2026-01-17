from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Date, DateTime, Table
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

# =========================
# ASSOCIATION TABLES
# =========================

dish_ingredient = Table(
    'dish_ingredient',
    Base.metadata,
    Column('dish_id', Integer, ForeignKey('dishes.id'), primary_key=True),
    Column('ingredient_id', Integer, ForeignKey('ingredients.id'), primary_key=True)
)

# =========================
# NATIONALITY
# =========================

class Nationality(Base):
    __tablename__ = "nationalities"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True)
    name = Column(String)
    bread_preference = Column(Float, default=1.0)
    dairy_preference = Column(Float, default=1.0)
    spice_tolerance = Column(Float, default=1.0)
    breakfast_style = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

# =========================
# GUEST
# =========================

class Guest(Base):
    __tablename__ = "guests"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True)
    nationality_id = Column(Integer, ForeignKey("nationalities.id"))
    dietary_restrictions = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    nationality = relationship("Nationality")

# =========================
# SUPPLIER
# =========================

class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    location = Column(String, nullable=True)
    distance_km = Column(Float, nullable=True)
    contact_phone = Column(String, nullable=True)
    specialization = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

# =========================
# SEASON (MUST BE BEFORE INGREDIENT)
# =========================

class Season(Base):
    __tablename__ = "seasons"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    months = Column(String, nullable=False)  # Store as JSON string: "[1,2,3]"
    score = Column(Float, default=1.0)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

# =========================
# INGREDIENT
# =========================

class Ingredient(Base):
    __tablename__ = "ingredients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    name_ar = Column(String, nullable=True)
    base_consumption_rate = Column(Float, default=1.0)
    unit = Column(String, default="kg")
    cost_per_unit = Column(Float, default=0.0)
    is_traditional = Column(Boolean, default=False)
    is_staple = Column(Boolean, default=False)
    season_id = Column(Integer, ForeignKey("seasons.id"), nullable=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    supplier = relationship("Supplier")
    season = relationship("Season", backref="ingredients")

# =========================
# DISH
# =========================

class Dish(Base):
    __tablename__ = "dishes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    name_ar = Column(String, nullable=True)
    description = Column(String, nullable=True)
    is_traditional = Column(Boolean, default=False)
    cuisine_type = Column(String, nullable=True)
    meal_type = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    reservations = relationship("Reservation", back_populates="dish")
    ingredients = relationship("Ingredient", secondary=dish_ingredient, backref="dishes")

# =========================
# WASTE LOG
# =========================

class WasteLog(Base):
    __tablename__ = "waste_logs"

    id = Column(Integer, primary_key=True, index=True)
    ingredient_id = Column(Integer, ForeignKey("ingredients.id"))
    quantity_kg = Column(Float)
    date = Column(Date)
    reason = Column(String, nullable=True)
    occupancy_on_date = Column(Integer, nullable=True)
    weather_condition = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    ingredient = relationship("Ingredient")

# =========================
# DISRUPTION EVENT
# =========================

class DisruptionEvent(Base):
    __tablename__ = "disruption_events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    event_type = Column(String, nullable=False)
    severity = Column(Float, nullable=False)
    occurred_at = Column(DateTime, nullable=False)
    description = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

# =========================
# RESERVATION
# =========================

class Reservation(Base):
    __tablename__ = "reservations"

    id = Column(Integer, primary_key=True, index=True)
    guest_id = Column(Integer, ForeignKey("guests.id"))
    dish_id = Column(Integer, ForeignKey("dishes.id"))
    date = Column(Date)
    quantity = Column(Integer, default=1)
    notes = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    dish = relationship("Dish", back_populates="reservations")
    guest = relationship("Guest")