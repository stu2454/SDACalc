# SDA Price Calculator

A web-based calculator for NDIS Specialist Disability Accommodation (SDA) pricing. This application allows users to calculate annual SDA payments based on stock type, building configuration, design features, and location.

## Features

- **Progressive Disclosure UI**: Step-by-step form that guides users through the calculation process
- **Real-time Validation**: Input validation based on NDIA business rules
- **Comprehensive Pricing**: Supports all SDA stock types, building types, and design categories
- **Location-Based Factors**: Applies geographic multipliers for 89 SA4 regions across Australia
- **MRRC Calculation**: Calculates Maximum Reasonable Rent Contribution for single and couple occupancy

## Technology Stack

- **Frontend**: React 18 + TypeScript + Vite + Tailwind CSS
- **Backend**: FastAPI (Python 3.11)
- **Database**: PostgreSQL 15
- **Deployment**: Docker + Docker Compose

## Prerequisites

- Docker Desktop installed
- Git
- VS Code (recommended)
- Node.js 18+ (for local frontend development without Docker)
- Python 3.11+ (for local backend development without Docker)

## Quick Start with Docker

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd sda-calculator
```

### 2. Copy Pricing Data

Place the extracted pricing data file in the `data` directory:

```bash
mkdir -p data
cp /path/to/base_prices_complete.csv data/
```

### 3. Start the Application

```bash
docker compose up --build
```

This will:
- Build and start PostgreSQL database
- Build and start FastAPI backend (port 8000)
- Build and start React frontend (port 3000)

### 4. Initialize the Database

In a new terminal, run:

```bash
docker compose exec backend python /app/init_db.py
```

This will create tables and load all reference data and pricing information.

### 5. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## Local Development (Without Docker)

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Set environment variable
export DATABASE_URL=postgresql://sda_user:sda_password@localhost:5432/sda_calculator

# Run the server
uvicorn main:app --reload
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

## Project Structure

```
sda-calculator/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── models.py            # SQLAlchemy database models
│   ├── schemas.py           # Pydantic schemas
│   ├── database.py          # Database connection
│   ├── calculation.py       # Pricing calculation logic
│   ├── validation.py        # Business rule validation
│   ├── requirements.txt     # Python dependencies
│   └── Dockerfile           # Backend container
├── frontend/
│   ├── src/
│   │   ├── Calculator.tsx   # Main calculator component
│   │   ├── App.tsx         # App wrapper
│   │   ├── api.ts          # API client
│   │   ├── types.ts        # TypeScript definitions
│   │   └── main.tsx        # Entry point
│   ├── package.json         # Node dependencies
│   ├── Dockerfile          # Production frontend container
│   ├── Dockerfile.dev      # Development frontend container
│   └── nginx.conf          # Nginx configuration
├── database/
│   └── init_db.py          # Database initialization script
├── data/
│   └── base_prices_complete.csv  # Pricing data
├── docker compose.yml       # Local development orchestration
├── render.yaml             # Render.com deployment config
└── README.md               # This file
```

## API Endpoints

### Health Check
```
GET /api/v1/health
```

### Calculate Pricing
```
POST /api/v1/sda/calculate
```

Request body:
```json
{
  "stock_type": "POST_2023",
  "building_type": "Apartment, 1 bedroom, 1 resident",
  "design_category": "FA",
  "ooa_status": "NO_OOA",
  "fire_sprinklers": false,
  "itc_claimed": true,
  "sa4_region": "NSW - Sydney - Inner City"
}
```

### Get Options
```
GET /api/v1/sda/options?stock_type=POST_2023&building_type=...
```

### Get Building Types
```
GET /api/v1/sda/building-types?stock_type=POST_2023
```

### Get Regions
```
GET /api/v1/sda/regions
```

## Deployment to Render

### 1. Create GitHub Repository

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin <your-github-repo-url>
git push -u origin main
```

### 2. Deploy to Render

1. Log in to [Render.com](https://render.com)
2. Click "New +" → "Blueprint"
3. Connect your GitHub repository
4. Render will automatically detect `render.yaml` and create:
   - PostgreSQL database
   - Backend web service
   - Frontend web service

### 3. Initialize Database on Render

After deployment, run the database initialization:

1. Go to your backend service in Render
2. Click "Shell"
3. Run: `python init_db.py`

## Environment Variables

### Backend
- `DATABASE_URL`: PostgreSQL connection string (auto-configured in Docker/Render)

### Frontend
- `VITE_API_URL`: Backend API URL (auto-configured in Docker/Render)

## Data Updates

### Quarterly MRRC Updates

1. Update MRRC rates in `database/init_db.py`
2. Run migration or manual update:
   ```sql
   UPDATE mrrc_rates SET effective_to = '2025-06-30' WHERE effective_to IS NULL;
   INSERT INTO mrrc_rates (...) VALUES (...);
   ```

### Annual Pricing Updates

1. Extract new pricing data from Excel calculator
2. Replace `data/base_prices_complete.csv`
3. Run update script:
   ```bash
   docker compose exec backend python update_pricing.py
   ```

## Validation Rules

The calculator enforces these NDIA rules:

1. **Basic category** only available for Existing Stock
2. **Robust categories** not available for Apartments
3. **Basic category** only available without On-site Overnight Assistance
4. **Legacy stock** only with 6-10 resident building types
5. **GST/ITC options** only for Post-2023 New Builds

## Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

### Integration Tests
Test the calculator against Excel:
1. Run both Docker containers
2. Test with known Excel scenarios
3. Compare results

## Troubleshooting

### Database Connection Issues
```bash
docker compose down -v  # Remove volumes
docker compose up --build
```

### Port Already in Use
```bash
# Stop other services on ports 3000, 8000, or 5432
# Or modify ports in docker compose.yml
```

### Frontend Not Loading
- Check that backend is running: http://localhost:8000/api/v1/health
- Check browser console for errors
- Verify VITE_API_URL is correct

## License

© 2026 NDIA. Internal use only.

## Support

For issues or questions, contact the Markets Delivery Branch.
