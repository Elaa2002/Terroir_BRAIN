"""
Seed the database with realistic Tunisian guest house data
Run: python seed_data.py
"""

from database import SessionLocal, engine, Base
from models import *
from datetime import date, timedelta
import json  

# Create all tables
Base.metadata.create_all(bind=engine)

def seed_database():
    db = SessionLocal()
    
    print("🌱 Seeding database with Tunisian terroir data...")
    
    # 1. Create Seasons (✅ FIXED: Convert lists to JSON strings)
    seasons = [
        Season(name="Winter", months=json.dumps([12, 1, 2]), score=0.8),
        Season(name="Spring", months=json.dumps([3, 4, 5]), score=1.0),
        Season(name="Summer", months=json.dumps([6, 7, 8]), score=0.9),
        Season(name="Autumn", months=json.dumps([9, 10, 11]), score=0.95)
    ]
    db.add_all(seasons)
    db.commit()
    print("✓ Seasons created")
    
    # 2. Create Nationalities with cultural preferences
    nationalities = [
        Nationality(
            code="FRA", name="French",
            bread_preference=1.3, dairy_preference=1.2,
            spice_tolerance=0.8, breakfast_style="Continental"
        ),
        Nationality(
            code="DEU", name="German",
            bread_preference=1.5, dairy_preference=1.1,
            spice_tolerance=0.7, breakfast_style="Continental"
        ),
        Nationality(
            code="ITA", name="Italian",
            bread_preference=1.2, dairy_preference=0.9,
            spice_tolerance=1.0, breakfast_style="Mediterranean"
        ),
        Nationality(
            code="GBR", name="British",
            bread_preference=1.1, dairy_preference=1.0,
            spice_tolerance=0.6, breakfast_style="Full English"
        ),
        Nationality(
            code="USA", name="American",
            bread_preference=1.0, dairy_preference=1.3,
            spice_tolerance=0.8, breakfast_style="American"
        ),
        Nationality(
            code="TUN", name="Tunisian",
            bread_preference=1.4, dairy_preference=0.8,
            spice_tolerance=1.5, breakfast_style="Traditional"
        )
    ]
    db.add_all(nationalities)
    db.commit()
    print("✓ Nationalities created")
    
    # 3. Create Suppliers
    suppliers = [
        Supplier(
            name="Boulangerie Sidi Bou Said",
            location="Sidi Bou Said",
            distance_km=2.5,
            contact_phone="+216 71 123 456",
            specialization="Traditional breads"
        ),
        Supplier(
            name="Marché Central Tunis",
            location="Tunis Medina",
            distance_km=5.0,
            contact_phone="+216 71 234 567",
            specialization="Fresh produce"
        ),
        Supplier(
            name="Coopérative de Tozeur",
            location="Tozeur",
            distance_km=420,
            contact_phone="+216 76 345 678",
            specialization="Dates and dried fruits"
        ),
        Supplier(
            name="Fromagerie du Cap Bon",
            location="Nabeul",
            distance_km=65,
            contact_phone="+216 72 456 789",
            specialization="Dairy products"
        ),
        Supplier(
            name="Port de Pêche La Goulette",
            location="La Goulette",
            distance_km=15,
            contact_phone="+216 71 567 890",
            specialization="Fresh fish"
        )
    ]
    db.add_all(suppliers)
    db.commit()
    print("✓ Suppliers created")
    
    # 4. Create Ingredients
    spring_season = db.query(Season).filter(Season.name == "Spring").first()
    summer_season = db.query(Season).filter(Season.name == "Summer").first()
    autumn_season = db.query(Season).filter(Season.name == "Autumn").first()
    winter_season = db.query(Season).filter(Season.name == "Winter").first()
    
    bread_supplier = suppliers[0]
    produce_supplier = suppliers[1]
    date_supplier = suppliers[2]
    dairy_supplier = suppliers[3]
    
    ingredients = [
        # Breads
        Ingredient(
            name="Tabouna Bread", name_ar="طابونة",
            base_consumption_rate=0.2, unit="kg", cost_per_unit=2.5,
            season_id=None, supplier_id=bread_supplier.id,
            is_traditional=True, is_staple=True
        ),
        Ingredient(
            name="Baguette", name_ar="باقيت",
            base_consumption_rate=0.15, unit="kg", cost_per_unit=1.5,
            season_id=None, supplier_id=bread_supplier.id,
            is_traditional=False, is_staple=True
        ),
        Ingredient(
            name="Malsouka Pastry", name_ar="ملسوقة",
            base_consumption_rate=0.05, unit="kg", cost_per_unit=4.0,
            season_id=None, supplier_id=bread_supplier.id,
            is_traditional=True, is_staple=False
        ),
        
        # Fruits
        Ingredient(
            name="Deglet Nour Dates", name_ar="دقلة نور",
            base_consumption_rate=0.08, unit="kg", cost_per_unit=8.0,
            season_id=autumn_season.id, supplier_id=date_supplier.id,
            is_traditional=True, is_staple=True
        ),
        Ingredient(
            name="Oranges (Maltaise)", name_ar="مالطية",
            base_consumption_rate=0.15, unit="kg", cost_per_unit=2.0,
            season_id=winter_season.id, supplier_id=produce_supplier.id,
            is_traditional=True, is_staple=False
        ),
        Ingredient(
            name="Clementines", name_ar="كليمونتين",
            base_consumption_rate=0.12, unit="kg", cost_per_unit=2.5,
            season_id=winter_season.id, supplier_id=produce_supplier.id,
            is_traditional=False, is_staple=False
        ),
        Ingredient(
            name="Watermelon", name_ar="دلاع",
            base_consumption_rate=0.25, unit="kg", cost_per_unit=1.5,
            season_id=summer_season.id, supplier_id=produce_supplier.id,
            is_traditional=True, is_staple=False
        ),
        
        # Dairy
        Ingredient(
            name="Yogurt (Rayeb)", name_ar="رايب",
            base_consumption_rate=0.1, unit="kg", cost_per_unit=3.0,
            season_id=None, supplier_id=dairy_supplier.id,
            is_traditional=True, is_staple=True
        ),
        Ingredient(
            name="Fresh Cheese", name_ar="جبن طري",
            base_consumption_rate=0.05, unit="kg", cost_per_unit=6.0,
            season_id=None, supplier_id=dairy_supplier.id,
            is_traditional=False, is_staple=False
        ),
        
        # Condiments & Spreads
        Ingredient(
            name="Olive Oil", name_ar="زيت زيتون",
            base_consumption_rate=0.03, unit="L", cost_per_unit=15.0,
            season_id=autumn_season.id, supplier_id=produce_supplier.id,
            is_traditional=True, is_staple=True
        ),
        Ingredient(
            name="Honey", name_ar="عسل",
            base_consumption_rate=0.02, unit="kg", cost_per_unit=20.0,
            season_id=None, supplier_id=produce_supplier.id,
            is_traditional=True, is_staple=True
        ),
        Ingredient(
            name="Harissa", name_ar="هريسة",
            base_consumption_rate=0.01, unit="kg", cost_per_unit=5.0,
            season_id=None, supplier_id=produce_supplier.id,
            is_traditional=True, is_staple=True
        ),
        
        # Eggs
        Ingredient(
            name="Eggs", name_ar="بيض",
            base_consumption_rate=0.12, unit="kg", cost_per_unit=4.0,
            season_id=None, supplier_id=produce_supplier.id,
            is_traditional=False, is_staple=True
        ),
    ]
    db.add_all(ingredients)
    db.commit()
    print("✓ Ingredients created")
    
    # 5. Create Traditional Dishes
    tabouna = db.query(Ingredient).filter(Ingredient.name == "Tabouna Bread").first()
    eggs = db.query(Ingredient).filter(Ingredient.name == "Eggs").first()
    harissa = db.query(Ingredient).filter(Ingredient.name == "Harissa").first()
    malsouka = db.query(Ingredient).filter(Ingredient.name == "Malsouka Pastry").first()
    olive_oil = db.query(Ingredient).filter(Ingredient.name == "Olive Oil").first()
    
    dishes = [
        Dish(
            name="Malsouka with Eggs",
            name_ar="ملسوقة بالبيض",
            description="Traditional Tunisian breakfast pastry with eggs",
            is_traditional=True,
            cuisine_type="Tunisian",
            meal_type="Breakfast"
        ),
        Dish(
            name="Continental Breakfast",
            name_ar="فطور أوروبي",
            description="Baguette with butter and jam",
            is_traditional=False,
            cuisine_type="Continental",
            meal_type="Breakfast"
        ),
        Dish(
            name="Tabouna with Olive Oil & Harissa",
            name_ar="طابونة بزيت الزيتون والهريسة",
            description="Traditional Tunisian breakfast",
            is_traditional=True,
            cuisine_type="Tunisian",
            meal_type="Breakfast"
        )
    ]
    
    # Link dishes to ingredients
    dishes[0].ingredients = [malsouka, eggs, harissa]
    dishes[2].ingredients = [tabouna, olive_oil, harissa]
    
    db.add_all(dishes)
    db.commit()
    print("✓ Dishes created")
    
    # 6. Create sample guests
    fra_nat = db.query(Nationality).filter(Nationality.code == "FRA").first()
    deu_nat = db.query(Nationality).filter(Nationality.code == "DEU").first()
    
    guests = [
        Guest(
            name="Marie Dubois",
            email="marie.dubois@example.com",
            nationality_id=fra_nat.id,
            dietary_restrictions="Vegetarian"
        ),
        Guest(
            name="Hans Mueller",
            email="hans.mueller@example.com",
            nationality_id=deu_nat.id,
            dietary_restrictions=None
        )
    ]
    db.add_all(guests)
    db.commit()
    print("✓ Guests created")
    
    # 7. Create disruption events (✅ FIXED: Use correct field names)
    events = [
        DisruptionEvent(
            title="Eid al-Fitr",  # ✅ Changed from 'name'
            event_type="Holiday",
            occurred_at=date(2025, 4, 10),  # ✅ Changed from 'date'
            severity=0.7,  # ✅ Changed from 'impact_factor'
            description="End of Ramadan - lighter breakfast demand"
        ),
        DisruptionEvent(
            title="Heatwave",
            event_type="Weather",
            occurred_at=date(2025, 7, 15),
            severity=0.8,
            description="Extreme heat reduces appetite"
        )
    ]
    db.add_all(events)
    db.commit()
    print("✓ Disruption events created")
    
    # 8. Create sample waste logs
    today = date.today()
    waste_logs = [
        WasteLog(
            ingredient_id=tabouna.id,
            quantity_kg=1.5,
            date=today - timedelta(days=7),
            reason="Flight delay - guests arrived late",
            occupancy_on_date=15,
            weather_condition="Normal"
        ),
        WasteLog(
            ingredient_id=eggs.id,
            quantity_kg=0.5,
            date=today - timedelta(days=3),
            reason="Over-preparation",
            occupancy_on_date=12,
            weather_condition="Hot"
        )
    ]
    db.add_all(waste_logs)
    db.commit()
    print("✓ Waste logs created")
    
    db.close()
    print("\n✅ Database seeded successfully!")
    print("\n📊 Summary:")
    print(f"   • {len(seasons)} seasons")
    print(f"   • {len(nationalities)} nationality profiles")
    print(f"   • {len(suppliers)} suppliers")
    print(f"   • {len(ingredients)} ingredients")
    print(f"   • {len(dishes)} dishes")
    print(f"   • {len(guests)} sample guests")
    print(f"   • {len(events)} disruption events")
    print(f"   • {len(waste_logs)} waste logs")

if __name__ == "__main__":
    seed_database()