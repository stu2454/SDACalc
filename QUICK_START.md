# SDA Calculator - Quick Start Guide

## What You've Received

A complete, production-ready web application for calculating NDIS SDA pricing with:
- ✅ React + TypeScript frontend
- ✅ FastAPI Python backend
- ✅ PostgreSQL database
- ✅ Docker configuration for local development
- ✅ Render deployment configuration
- ✅ All 848 base price records pre-loaded
- ✅ Complete validation rules
- ✅ Progressive disclosure UI

## 5-Minute Local Setup

### 1. Extract the Archive
```bash
tar -xzf sda-calculator-app.tar.gz
cd sda-calculator
```

### 2. Run Setup Script
```bash
chmod +x setup.sh
./setup.sh
```

The script will:
- Check Docker installation
- Build all containers
- Initialize database with pricing data
- Start all services

### 3. Open Your Browser
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Deploy to Render (Free Hosting)

### 1. Create GitHub Repo
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/sda-calculator.git
git push -u origin main
```

### 2. Deploy to Render
1. Go to https://render.com
2. New+ → Blueprint
3. Connect your GitHub repo
4. Click "Apply"

### 3. Initialize Database
After deployment:
1. Open backend service in Render
2. Click "Shell" tab
3. Run: `python /app/database/init_db.py`

### 4. Done!
Your app is live at: `https://sda-calculator-frontend.onrender.com`

## Project Structure

```
sda-calculator/
├── backend/              # FastAPI application
│   ├── main.py          # API endpoints
│   ├── models.py        # Database models
│   ├── calculation.py   # Pricing logic
│   └── validation.py    # Business rules
├── frontend/            # React application
│   └── src/
│       ├── Calculator.tsx   # Main component
│       └── api.ts          # API client
├── database/
│   └── init_db.py       # Setup script
├── data/
│   └── base_prices_complete.csv  # 848 price records
├── docker compose.yml   # Local development
├── render.yaml         # Cloud deployment
└── setup.sh            # One-command setup
```

## Key Files

### Configuration
- `docker compose.yml` - Local development orchestration
- `render.yaml` - Render.com deployment config
- `.env.example` - Environment variables template

### Application Code
- `backend/main.py` - FastAPI app with all endpoints
- `backend/calculation.py` - Pricing calculation logic
- `frontend/src/Calculator.tsx` - React UI component

### Documentation
- `README.md` - Full documentation
- `DEPLOYMENT.md` - Detailed deployment guide
- `QUICK_START.md` - This file

## Test the Calculator

Try these scenarios to verify everything works:

### Test 1: Basic Existing Stock
- Stock Type: Existing Stock
- Building: Apartment, 1 bedroom, 1 resident
- Design: Basic
- OOA: Without OOA
- Sprinklers: No
- Region: NSW - Sydney - Inner City
- **Expected**: Should calculate successfully

### Test 2: Post-2023 with ITC
- Stock Type: Post-2023 New Build
- Building: House, 2 residents
- Design: Fully Accessible
- OOA: With OOA
- Sprinklers: Yes
- ITC: Claimed
- Region: VIC - Melbourne - Inner
- **Expected**: Should calculate successfully

### Test 3: Validation Error
- Stock Type: Post-2023 New Build
- Design: Basic
- **Expected**: Should show error "Basic only for Existing Stock"

## Common Commands

### Local Development
```bash
# Start services
docker compose up

# Stop services
docker compose down

# View logs
docker compose logs -f backend

# Rebuild after code changes
docker compose up --build

# Reset database
docker compose down -v
docker compose up
docker compose exec backend python /app/database/init_db.py
```

### Git Workflow
```bash
# Make changes
git add .
git commit -m "Description of changes"
git push origin main  # Automatically deploys to Render
```

## Troubleshooting

### "Port already in use"
```bash
# Stop other services using ports 3000, 8000, or 5432
docker compose down
lsof -ti:3000 -ti:8000 -ti:5432 | xargs kill -9
```

### "Database connection failed"
```bash
# Reset and reinitialize
docker compose down -v
docker compose up -d db
sleep 10
docker compose up -d backend frontend
docker compose exec backend python /app/database/init_db.py
```

### Frontend won't load
1. Check backend is running: http://localhost:8000/api/v1/health
2. Check browser console for errors
3. Rebuild containers: `docker compose up --build`

## Next Steps

1. ✅ Test locally with Docker
2. ✅ Deploy to Render
3. ✅ Run test calculations
4. ✅ Compare results with Excel
5. ✅ Document any discrepancies
6. ✅ Plan quarterly MRRC updates
7. ✅ Schedule annual pricing refresh

## Support Files

All technical analysis and documentation:
- `sda-pricing-brief.md` - Domain knowledge
- `sda-calculator-technical-analysis.md` - Implementation details
- `sda-formula-analysis.md` - Excel formula documentation
- `sda-project-complete-summary.md` - Complete project overview

## Need Help?

1. Check `README.md` for full documentation
2. Check `DEPLOYMENT.md` for deployment issues
3. Review logs: `docker compose logs -f`
4. Contact Markets Delivery Branch

---

**You're ready to go!** Run `./setup.sh` and start calculating SDA pricing.
