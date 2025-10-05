# Vercel Deployment Guide

This guide will help you deploy your Stormhack project to Vercel.

## Project Structure

This project consists of:
- **Frontend**: React + TypeScript + Vite application
- **Backend**: Flask API with PostgreSQL database

## Deployment Options

### Option 1: Deploy Frontend Only to Vercel (Recommended for MVP)

This is the simplest approach for getting started quickly.

#### Steps:

1. **Deploy Frontend to Vercel**:
   ```bash
   cd frontend
   vercel --prod
   ```

2. **Set Environment Variables in Vercel Dashboard**:
   - `VITE_API_URL`: Your backend API URL (e.g., `https://your-backend.herokuapp.com` or `https://your-backend.railway.app`)

3. **Deploy Backend Separately**:
   - Consider deploying to Heroku, Railway, or Render for the backend
   - Update the `FRONTEND_ORIGINS` environment variable to include your Vercel frontend URL

### Option 2: Deploy Both Frontend and Backend to Vercel

This approach uses Vercel's serverless functions for the backend.

#### Steps:

1. **Set up Environment Variables in Vercel Dashboard**:
   ```
   JWT_SECRET_KEY=your-super-secret-jwt-key-here
   POSTGRES_HOST=your-postgres-host
   POSTGRES_USER=your-postgres-user
   POSTGRES_PASSWORD=your-postgres-password
   POSTGRES_DB=your-postgres-database
   FRONTEND_ORIGINS=https://your-app.vercel.app
   ```

2. **Deploy the Entire Project**:
   ```bash
   vercel --prod
   ```

3. **Configure Database**:
   - Set up a PostgreSQL database (recommended: Neon, Supabase, or PlanetScale)
   - Run the database initialization script from `database/init.sql`

## Environment Variables

### Frontend (.env)
```env
VITE_API_URL=https://your-backend-domain.vercel.app
```

### Backend
```env
JWT_SECRET_KEY=your-super-secret-jwt-key-here
POSTGRES_HOST=your-postgres-host
POSTGRES_USER=your-postgres-user
POSTGRES_PASSWORD=your-postgres-password
POSTGRES_DB=your-postgres-database
FRONTEND_ORIGINS=https://your-frontend-domain.vercel.app
JWT_ACCESS_TOKEN_EXPIRES_SECONDS=86400
```

## Database Setup

1. **Create a PostgreSQL database** on your preferred provider (Neon, Supabase, etc.)
2. **Run the initialization script**:
   ```bash
   psql -h your-host -U your-user -d your-db -f database/init.sql
   ```
3. **Update environment variables** with your database credentials

## Build Configuration

The project is already configured with:
- ✅ Vercel configuration files (`vercel.json`)
- ✅ Optimized Vite build settings
- ✅ Centralized API endpoint configuration
- ✅ Environment variable support

## Troubleshooting

### Common Issues:

1. **CORS Errors**:
   - Ensure `FRONTEND_ORIGINS` includes your Vercel domain
   - Check that the frontend URL is correct

2. **Database Connection Issues**:
   - Verify database credentials
   - Ensure your database allows connections from Vercel's IP ranges

3. **Build Failures**:
   - Check that all dependencies are properly specified
   - Ensure environment variables are set correctly

### Testing Locally:

1. **Frontend**:
   ```bash
   cd frontend
   npm run dev
   ```

2. **Backend**:
   ```bash
   cd backend
   python app/app.py
   ```

## Production Checklist

- [ ] Environment variables configured
- [ ] Database initialized and accessible
- [ ] CORS origins updated
- [ ] JWT secret key is secure
- [ ] Frontend builds successfully
- [ ] Backend deploys without errors
- [ ] API endpoints respond correctly
- [ ] Authentication flow works
- [ ] Database connections are stable

## Next Steps

After deployment:
1. Test all functionality
2. Set up monitoring (Vercel Analytics)
3. Configure custom domain if needed
4. Set up CI/CD for automatic deployments
5. Consider implementing caching strategies

## Support

For issues specific to this deployment:
1. Check the Vercel deployment logs
2. Verify environment variables
3. Test API endpoints independently
4. Check database connectivity
