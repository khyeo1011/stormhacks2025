#!/bin/bash

# Stormhack Vercel Deployment Script

echo "🚀 Starting Stormhack deployment to Vercel..."

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "❌ Vercel CLI not found. Please install it first:"
    echo "npm i -g vercel"
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "vercel.json" ]; then
    echo "❌ vercel.json not found. Please run this script from the project root."
    exit 1
fi

echo "📋 Deployment options:"
echo "1. Deploy frontend only (recommended for MVP)"
echo "2. Deploy full stack (frontend + backend)"
echo "3. Deploy backend only"
read -p "Choose option (1-3): " choice

case $choice in
    1)
        echo "🎨 Deploying frontend only..."
        cd frontend
        vercel --prod
        echo "✅ Frontend deployed! Don't forget to set VITE_API_URL environment variable."
        ;;
    2)
        echo "🌐 Deploying full stack..."
        vercel --prod
        echo "✅ Full stack deployed! Make sure to configure all environment variables."
        ;;
    3)
        echo "⚙️ Deploying backend only..."
        cd backend
        vercel --prod
        echo "✅ Backend deployed! Make sure to configure database environment variables."
        ;;
    *)
        echo "❌ Invalid option. Please choose 1, 2, or 3."
        exit 1
        ;;
esac

echo ""
echo "📚 Next steps:"
echo "1. Set up environment variables in Vercel dashboard"
echo "2. Configure your database"
echo "3. Test your deployment"
echo "4. Check the DEPLOYMENT.md file for detailed instructions"
echo ""
echo "🎉 Deployment completed!"
