# 🧠 The Terroir Brain API

<div align="center">

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.11-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green.svg)
![Docker](https://img.shields.io/badge/docker-ready-brightgreen.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

**Cultural Demand Forecasting & Waste Reduction System for Tunisian Guest Houses**

[Features](#-features) • [Quick Start](#-quick-start) • [Documentation](#-documentation) • [API Reference](#-api-reference) • [Contributing](#-contributing)

</div>

---

## 📖 Overview

The **Terroir Brain API** is a microservices-based REST API that solves Tunisia's **197 million USD annual food waste problem** in the hospitality industry. Unlike generic property management systems, our solution embeds **Tunisian terroir intelligence** into demand forecasting, using a multi-factor formula that incorporates:

- 🌍 **Cultural preferences** (nationality-based consumption patterns)
- 🌿 **Seasonality** (local agricultural cycles)
- 📅 **Disruption events** (weather, holidays, transportation)
- ♻️ **Waste feedback loops** (learning from historical patterns)
- 🏪 **Local sourcing** (supplier proximity and sustainability)

### The Problem

- **58%** of Tunisia's food waste is organic material
- **Breakfast** represents the highest waste category in guest houses
- Traditional hospitality (*Baraka*) conflicts with modern sustainability
- No intelligent systems connect guest profiles, seasonal ingredients, and waste patterns

### The Solution

A transparent, explainable forecasting system that:
- ✅ Reduces food waste by **27-40%**
- ✅ Saves **600+ TND monthly** per guest house
- ✅ Achieves **76.9% local sourcing**
- ✅ Preserves Tunisian culinary heritage
- ✅ Provides **100% explainable** predictions (no black-box AI)

---

## 🎯 Key Features

### Intelligence Engines

#### 🔮 Forecast Engine
- **Multi-factor demand prediction** using transparent formula
- **Cultural preference modeling** (bread, dairy, spice tolerance)
- **Seasonal awareness** (Tunisian agricultural cycles)
- **Disruption adjustments** (heatwaves, holidays, flight delays)
- **Waste feedback loops** (reduce forecasts for frequently wasted items)
- **Explainable predictions** (shows calculation breakdown)

#### 🍽️ Cultural Menu Engine
- **Dynamic menu generation** based on seasonality and nationality
- **Traditional dish prioritization** (preserving Tunisian heritage)
- **Multi-criteria justification** (tradition, seasonality, cost, locality)
- **Cultural context notes** (breakfast style preferences)
- **Sustainability scoring** (seasonal compliance percentage)

#### 📊 Waste Analyzer
- **Pattern recognition** (identifies top wasted items)
- **Root cause analysis** (groups waste by reason)
- **Trend tracking** (weekly comparison, increasing/decreasing)
- **Cost impact calculation** (TND lost to waste)
- **Actionable recommendations** (flight tracking, weather adjustments, portion control)

### Advanced Analytics (7 Endpoints)

1. **🛒 Procurement Optimizer**
   - Multi-day, multi-nationality shopping lists
   - Bulk purchase discounts (10% @ 10kg, 15% @ 20kg)
   - Carbon footprint tracking
   - Waste risk assessment
   - Local sourcing percentage

2. **📊 Nationality Comparison Matrix**
   - Cross-nationality demand analysis
   - Cost comparisons
   - Preference visualization

3. **💡 Waste Impact Simulator**
   - Strategy testing (reduce bread 20%, flight tracking, weather)
   - ROI projections
   - Savings calculations

4. **👨‍🍳 Kitchen Dashboard**
   - Real-time prep requirements
   - Today's alerts and warnings
   - High-risk item flagging

5. **🌿 Seasonal Optimizer**
   - Menu seasonality scoring
   - Optimization recommendations
   - Sustainability metrics

6. **💰 Cost-Benefit Analysis**
   - Financial impact over 30-90 days
   - Break-even timeline
   - Comprehensive ROI

7. **🌍 Cultural Insights**
   - Preference matrices for all nationalities
   - Compatibility analysis (best/worst pairs to host together)
   - Diversity requirements

---

## 🏗️ Architecture

### Microservices Design

```
┌─────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                          │
│  Web Apps • Mobile Apps • API Testing Tools (Insomnia)      │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                     API GATEWAY LAYER                        │
│  ┌──────────────────┐         ┌──────────────────┐         │
│  │  terroir_api     │         │  terroir_auth    │         │
│  │  Port 8000       │         │  Port 8001       │         │
│  │  - 80+ Endpoints │         │  - JWT Auth      │         │
│  └──────────────────┘         └──────────────────┘         │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                   BUSINESS LOGIC LAYER                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │  Forecast   │  │  Cultural   │  │    Waste    │        │
│  │   Engine    │  │   Engine    │  │  Analyzer   │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    DATA ACCESS LAYER                         │
│        SQLAlchemy ORM • Pydantic Validation                  │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                      DATABASE LAYER                          │
│  SQLite (Development) • PostgreSQL (Production Ready)        │
└─────────────────────────────────────────────────────────────┘
```

### Technology Stack

| **Layer** | **Technology** | **Purpose** |
|-----------|---------------|-------------|
| Backend | FastAPI (Python 3.11) | High-performance async API |
| Database | SQLite + SQLAlchemy | ORM with relationship management |
| Validation | Pydantic v2 | Request/response validation |
| Containerization | Docker + Docker Compose | Microservices orchestration |
| Authentication | JWT | Secure token-based auth |
| API Docs | OpenAPI/Swagger | Auto-generated documentation |
| Testing | Insomnia | Comprehensive endpoint testing |

### Database Models (9 Core Entities)

- **Nationality** - Cultural preference profiles
- **Guest** - Guest information and dietary restrictions
- **Supplier** - Local ingredient suppliers with distance tracking
- **Season** - Seasonal periods for ingredient availability
- **Ingredient** - Food items with terroir data
- **Dish** - Menu items with ingredient relationships
- **WasteLog** - Historical waste tracking
- **DisruptionEvent** - Events affecting demand (weather, holidays)
- **Reservation** - Guest bookings

[View Full Database Schema](docs/diagrams/er-diagram.md)

---

## 🚀 Quick Start

### Prerequisites

- Docker Desktop (Windows/Mac) or Docker Engine (Linux)
- Docker Compose v2.0+
- 2GB free disk space
- Ports 8000 and 8001 available

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/terroir-brain-api.git
cd terroir-brain-api
```

2. **Configure environment variables**
```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your settings (optional for development)
```

3. **Build and start Docker containers**
```bash
docker-compose up --build
```

4. **Wait for startup** (you'll see):
```
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

5. **Seed the database**
```bash
# In a new terminal
docker exec -it terroir_api python seed_data.py
```

Expected output:
```
🌱 Seeding database with Tunisian terroir data...
✓ Seasons created
✓ Nationalities created
✓ Suppliers created
✓ Ingredients created
✓ Dishes created
✓ Guests created
✓ Disruption events created
✓ Waste logs created

✅ Database seeded successfully!
```

6. **Access the API**
- **API Server:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs
- **Auth Server:** http://localhost:8001

---

## 📚 Documentation

### API Documentation

Access the interactive Swagger UI at:
```
http://localhost:8000/docs
```

### Core Endpoints

#### Intelligence Endpoints

```bash
# Procurement Optimizer
POST /intelligence/procurement-optimizer
?start_date=2025-01-13&end_date=2025-01-16

# Nationality Comparison
GET /intelligence/nationality-comparison
?occupancy=15&date=2025-01-13

# Waste Impact Simulator
POST /intelligence/waste-simulator

# Kitchen Dashboard
GET /intelligence/kitchen-dashboard

# Seasonal Optimizer
POST /intelligence/seasonal-optimizer

# Cost-Benefit Analysis
POST /intelligence/cost-benefit

# Cultural Insights
GET /intelligence/cultural-insights
```

#### Forecast Endpoints

```bash
# Get ingredient demand forecast
GET /forecast/?occupancy=15&nationality=FRA&target_date=2025-01-10

# Explain forecast calculation
GET /forecast/explain/1?occupancy=15&nationality_code=FRA
```

#### Menu Generation

```bash
# Generate seasonal menu
GET /menu/?month=1&nationality=FRA

# Justify dish recommendation
GET /menu/justify/3
```

#### Waste Analysis

```bash
# Get waste analysis and recommendations
GET /waste-analysis/?days=30

# Get waste trends
GET /waste-analysis/trends?days=30
```

#### Breakfast Recommendations

```bash
# Get nationality-specific breakfast items
GET /recommendations/breakfast/FRA
```

### CRUD Operations

All 9 resources support full CRUD operations:
- `GET /{resource}/` - List all
- `GET /{resource}/{id}` - Get by ID
- `POST /{resource}/` - Create
- `PUT /{resource}/{id}` - Full update
- `PATCH /{resource}/{id}` - Partial update
- `DELETE /{resource}/{id}` - Delete

Resources: `nationalities`, `guests`, `ingredients`, `dishes`, `suppliers`, `disruptions`, `waste-logs`, `reservations`, `seasons`

---

## 🧪 Testing

### Run All Tests

The project includes **96 comprehensive test cases** covering all endpoints.

```bash
# Import Insomnia collection
# File: insomnia_collection.json

# Or use curl/httpie for individual tests
curl http://localhost:8000/forecast/?occupancy=15&nationality=FRA
```

### Test Coverage

| **Category** | **Test Cases** | **Status** |
|-------------|---------------|-----------|
| Intelligence Endpoints | 7 | ✓ 100% Pass |
| Forecast Endpoints | 5 | ✓ 100% Pass |
| Menu Generation | 4 | ✓ 100% Pass |
| Waste Analysis | 3 | ✓ 100% Pass |
| CRUD Operations | 54 | ✓ 100% Pass |
| Authentication | 8 | ✓ 100% Pass |
| Error Handling | 15 | ✓ 100% Pass |
| **TOTAL** | **96** | **✓ 100%** |

---

## 📊 The Forecasting Formula

### Multi-Factor Demand Equation

```
Demand = Occupancy × BaseRate × Seasonality × Culture × Disruption × Waste
```

**Where:**
- **Occupancy (O)** = Number of guests
- **Base Rate (B)** = kg per person (from ingredient data)
- **Seasonality (S)** = 0.5-1.0 (season score)
- **Culture (C)** = 0.0-2.0 (nationality preference)
- **Disruption (E)** = 0.0-1.0 (event impact, e.g., heatwave severity)
- **Waste (W)** = 0.85-1.0 (feedback loop adjustment)

### Example Calculation

**Scenario:** 15 French guests on January 10, 2025, requesting Tabouna Bread

```python
# Step-by-step calculation
Occupancy = 15 guests
Base_Rate = 0.2 kg/person

Step 1: Base demand
15 × 0.2 = 3.0 kg

Step 2: Apply seasonality (Winter, non-seasonal item)
3.0 × 0.8 = 2.4 kg

Step 3: Apply cultural preference (French bread preference = 1.3)
2.4 × 1.3 = 3.12 kg

Step 4: Apply disruption factor (no events = 1.0)
3.12 × 1.0 = 3.12 kg

Step 5: Apply waste adjustment (bread frequently wasted = 0.85)
3.12 × 0.85 = 2.65 kg

# Final Recommendation: 2.65 kg Tabouna Bread
```

**Interpretation:** The system recommends **2.65 kg** because French guests prefer more bread (+30%), but historical waste data shows bread is often wasted (-15%), so the forecast is adjusted down.

---

## 🎨 Project Structure

```
terroir-brain-api/
├── api-server/                 # Main API microservice
│   ├── services/               # Intelligence engines
│   │   ├── __init__.py
│   │   ├── forecast.py         # Forecast Engine
│   │   ├── cultural.py         # Cultural Menu Engine
│   │   └── waste.py            # Waste Analyzer
│   ├── data/                   # SQLite database
│   ├── main.py                 # FastAPI app + routes
│   ├── models.py               # SQLAlchemy ORM models
│   ├── schemas.py              # Pydantic schemas
│   ├── database.py             # Database configuration
│   ├── seed_data.py            # Database seeding script
│   ├── requirements.txt        # Python dependencies
│   └── Dockerfile              # API server container
│
├── auth-server/                # Authentication microservice
│   ├── main.py                 # Auth routes (login, register)
│   ├── models.py               # User model
│   ├── schemas.py              # Auth schemas
│   ├── auth.py                 # JWT utilities
│   ├── database.py             # Auth database
│   ├── requirements.txt
│   └── Dockerfile
│
├── data/                       # Persistent storage
│   ├── api/
│   │   └── terroir.db          # Main database
│   └── auth/
│       └── auth.db             # Auth database
│
├── docs/                       # Documentation
│   ├── diagrams/               # Mermaid diagrams
│   ├── api-reference.md        # Complete API docs
│   └── deployment.md           # Deployment guide
│
├── insomnia_collection.json    # API test collection
├── docker-compose.yml          # Container orchestration
├── .env.example                # Environment variables template
├── .gitignore
├── LICENSE
└── README.md                   # This file
```

---

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# API Server Configuration
API_SERVER_HOST=0.0.0.0
API_SERVER_PORT=8000
DATABASE_URL=sqlite:///./data/terroir.db

# Auth Server Configuration
AUTH_SERVER_HOST=0.0.0.0
AUTH_SERVER_PORT=8001
AUTH_DATABASE_URL=sqlite:///./data/auth.db

# JWT Configuration
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS Configuration (optional)
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
```

### Docker Compose Configuration

The `docker-compose.yml` orchestrates both microservices:

```yaml
version: '3.8'
services:
  terroir_api:
    build: ./api-server
    container_name: terroir_api
    ports:
      - "8000:8000"
    volumes:
      - ./data/api:/app/data
      - ./api-server:/app
    environment:
      - DATABASE_URL=sqlite:///./data/terroir.db

  terroir_auth:
    build: ./auth-server
    container_name: terroir_auth
    ports:
      - "8001:8001"
    volumes:
      - ./data/auth:/app/data
      - ./auth-server:/app
    environment:
      - DATABASE_URL=sqlite:///./data/auth.db
      - SECRET_KEY=${SECRET_KEY}
```

---

## 📈 Performance & Impact

### Projected Impact Metrics

| **Metric** | **Before** | **After** | **Improvement** |
|-----------|----------|---------|----------------|
| Monthly Waste | 2.0 kg | 1.2 kg | **40.2% reduction** |
| Monthly Cost | 302.5 TND | 181.0 TND | **121.5 TND savings** |
| Annual Savings | 0 TND | 1,458 TND | **ROI < 3 months** |
| Local Sourcing | ~40% | 76.9% | **+36.9%** |
| Carbon Footprint | Baseline | -18.1 kg CO₂/month | **40% reduction** |
| Seasonal Compliance | ~50% | 85% | **+35%** |

### User Study Results (N=5 guest house managers)

- ✅ **100%** understood forecast explanations
- ✅ **100%** trusted recommendations over manual estimation
- ✅ **80%** would implement the system
- ✅ **2.5 minutes** average decision time (vs. 15 minutes manual)


### Scaling Considerations

For production with 100+ guest houses:
- ✅ Migrate to PostgreSQL
- ✅ Add Redis caching
- ✅ Implement load balancing
- ✅ Set up monitoring (Prometheus/Grafana)
- ✅ Add logging aggregation (ELK stack)
- ✅ Database connection pooling
- ✅ API rate limiting


## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **Commit your changes** (`git commit -m 'Add amazing feature'`)
4. **Push to the branch** (`git push origin feature/amazing-feature`)
5. **Open a Pull Request**

### Contribution Guidelines

- Follow PEP 8 style guide for Python code
- Add tests for new features
- Update documentation
- Keep commits atomic and well-described
- Ensure all tests pass before submitting PR

---

## 🙏 Acknowledgments

- **Academic Supervisor:** Montassar Ben Messaoud, PhD
- **Institution:** Tunis Business School
- **Tunisian Guest House Managers:** For valuable feedback and validation
- **FastAPI Community:** For excellent documentation and support

---

## 📞 Contact & Support

- **Author:** Elaa Marco
- **Email:** ella.marco.tn@gmail.com
- **LinkedIn:** https://www.linkedin.com/in/elaamarco/


## 🗺️ Roadmap

### Phase 1: Core Features (✅ Completed)
- ✅ Multi-factor forecasting formula
- ✅ Cultural menu generation
- ✅ Waste analysis
- ✅ 7 advanced intelligence endpoints
- ✅ Docker deployment
- ✅ Comprehensive testing

### Phase 2: Integrations (🚧 In Progress)
- ⏳ Flight tracking API integration
- ⏳ Weather API for auto-disruptions
- ⏳ Supplier inventory sync
- ⏳ Payment gateway integration

### Phase 3: Mobile & UX (📅 Planned)
- 📱 Mobile app for kitchen staff
- 🌐 Multi-language support (Arabic, French, English)
- 📊 Advanced dashboard with charts
- 🔔 Real-time notifications

### Phase 4: AI Enhancement (🔮 Future)
- 🤖 ML augmentation (keep explainable baseline)
- 📈 Time series trend prediction
- 🎯 Anomaly detection
- 🧪 A/B testing framework

---

## 📊 Project Statistics

- **Lines of Code:** ~5,000
- **API Endpoints:** 80+
- **Database Models:** 9
- **Test Cases:** 96
- **Test Coverage:** 100%
- **Docker Containers:** 2
- **Development Time:** 3 months
- **Contributors:** 1 (looking for more!)

---

<div align="center">

**⭐ Star this repo if you find it useful!**

**Made with ❤️ for Tunisian hospitality and sustainability**


</div>
