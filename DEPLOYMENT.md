# SDA Calculator - Deployment Guide

## Overview

This guide covers deploying the SDA Calculator to Render.com from a GitHub repository.

## Prerequisites

- GitHub account
- Render.com account (free tier is sufficient)
- Git installed locally
- Completed local testing

## Step-by-Step Deployment

### 1. Prepare Your Local Repository

```bash
# Navigate to project directory
cd sda-calculator

# Ensure all changes are committed
git status

# If there are uncommitted changes:
git add .
git commit -m "Prepare for deployment"
```

### 2. Create GitHub Repository

#### Option A: Using GitHub CLI
```bash
gh repo create sda-calculator --public --source=. --remote=origin
git push -u origin main
```

#### Option B: Using GitHub Web Interface
1. Go to https://github.com/new
2. Repository name: `sda-calculator`
3. Choose Public or Private
4. Don't initialize with README (we already have one)
5. Click "Create repository"
6. Follow the commands to push existing repository:

```bash
git remote add origin https://github.com/YOUR_USERNAME/sda-calculator.git
git branch -M main
git push -u origin main
```

### 3. Deploy to Render

#### Step 3.1: Connect GitHub
1. Log in to [Render.com](https://render.com)
2. Click "New +" in the top right
3. Select "Blueprint"
4. Click "Connect GitHub" (if not already connected)
5. Authorize Render to access your repositories

#### Step 3.2: Select Repository
1. Find `sda-calculator` in the repository list
2. Click "Connect"
3. Render will automatically detect `render.yaml`

#### Step 3.3: Review Blueprint
Render will show you the services it will create:
- **sda-calculator-db**: PostgreSQL database (Free tier: 256MB RAM, 1GB storage)
- **sda-calculator-backend**: FastAPI backend (Free tier: 512MB RAM)
- **sda-calculator-frontend**: React frontend (Free tier: 512MB RAM)

Click "Apply" to create all services.

#### Step 3.4: Wait for Deployment
- Database usually deploys in ~2 minutes
- Backend and frontend will follow (5-10 minutes each)
- Watch the build logs for any errors

### 4. Initialize Database

Once the backend is deployed:

1. Go to the backend service in Render dashboard
2. Click the "Shell" tab
3. Run the initialization command:
```bash
python /app/database/init_db.py
```

4. Wait for confirmation message:
```
DATABASE INITIALIZATION COMPLETE
```

### 5. Verify Deployment

#### Test Backend
1. Find your backend URL (e.g., `https://sda-calculator-backend.onrender.com`)
2. Visit: `https://YOUR-BACKEND-URL/api/v1/health`
3. Should return: `{"status": "healthy", "database": "connected"}`

#### Test Frontend
1. Find your frontend URL (e.g., `https://sda-calculator-frontend.onrender.com`)
2. Visit the URL
3. Complete a test calculation

### 6. Configure Custom Domain (Optional)

1. In Render dashboard, go to your frontend service
2. Click "Settings" → "Custom Domain"
3. Add your domain (e.g., `sda-calculator.yourdomain.com`)
4. Update your DNS with the provided CNAME record

## Environment Variables

Render automatically configures these from `render.yaml`:

### Backend
- `DATABASE_URL`: Auto-configured from database service

### Frontend
- `VITE_API_URL`: Auto-configured from backend service

To add custom environment variables:
1. Go to service → Settings → Environment
2. Add key-value pairs
3. Click "Save Changes"
4. Service will automatically redeploy

## Updating the Application

### Deploy Code Changes
```bash
# Make your changes
git add .
git commit -m "Your update message"
git push origin main
```

Render will automatically detect the push and redeploy.

### Update Pricing Data

1. Update `data/base_prices_complete.csv` locally
2. Commit and push:
```bash
git add data/base_prices_complete.csv
git commit -m "Update pricing data for FY 2026-27"
git push origin main
```

3. After deployment, run update script in backend shell:
```bash
python /app/update_pricing.py
```

### Manual Redeploy
If needed, you can trigger manual redeployment:
1. Go to service in Render dashboard
2. Click "Manual Deploy" → "Deploy latest commit"

## Monitoring

### View Logs
1. Go to service in Render dashboard
2. Click "Logs" tab
3. Select time range and filter level

### View Metrics
1. Go to service → Metrics
2. View CPU, Memory, and Request metrics
3. Set up alerts if needed

## Troubleshooting

### Database Connection Issues
1. Check database service is running
2. Verify `DATABASE_URL` environment variable
3. Check database logs for errors
4. Ensure database has been initialized

### Build Failures

#### Backend Build Fails
- Check requirements.txt for typos
- Verify Python version compatibility
- Check backend/Dockerfile syntax

#### Frontend Build Fails
- Check package.json for correct dependencies
- Verify Node.js version
- Check frontend/Dockerfile syntax
- Ensure all TypeScript types are correct

### Performance Issues

#### Free Tier Limitations
- Services spin down after 15 minutes of inactivity
- First request after spin-down takes ~1 minute
- Limited to 512MB RAM per service

#### Upgrade Options
1. Go to service → Settings
2. Change Instance Type:
   - Starter: $7/month (512MB RAM, no spin-down)
   - Standard: $25/month (2GB RAM)
   - Pro: $85/month (4GB RAM)

## Backup and Recovery

### Database Backups

#### Manual Backup
1. Go to database service → Settings
2. Click "Snapshots"
3. Click "Create Snapshot"

#### Automated Backups
Render automatically backs up PostgreSQL daily (retained for 7 days).

### Restore from Backup
1. Go to database → Snapshots
2. Select snapshot
3. Click "Restore"
4. Confirm restoration

### Export Database
```bash
# From Render shell
pg_dump $DATABASE_URL > backup.sql
```

## Cost Estimates

### Free Tier (Limited)
- Database: Free (256MB, 1GB storage)
- Backend: Free (512MB, spins down)
- Frontend: Free (512MB, spins down)
- **Total: $0/month**

### Starter Tier (Recommended for Production)
- Database: Free (sufficient for this app)
- Backend: Starter ($7/month)
- Frontend: Starter ($7/month)
- **Total: $14/month**

### Professional Tier
- Database: Standard ($7/month, 1GB RAM)
- Backend: Standard ($25/month)
- Frontend: Standard ($25/month)
- **Total: $57/month**

## Security Considerations

### Free Tier SSL
All Render services include free SSL certificates (HTTPS).

### Environment Variables
Never commit sensitive data to Git. Use Render's environment variable system.

### Database Security
- Database is only accessible from Render services
- Automatic encrypted connections
- Regular security patches

## Support

### Render Support
- Documentation: https://render.com/docs
- Community: https://community.render.com
- Status: https://status.render.com

### Application Issues
- Check GitHub Issues
- Review application logs
- Contact Markets Delivery Branch

## Next Steps

After successful deployment:
1. ✅ Test all calculations match Excel
2. ✅ Set up monitoring alerts
3. ✅ Document update procedures
4. ✅ Schedule quarterly MRRC updates
5. ✅ Plan annual pricing refresh process
