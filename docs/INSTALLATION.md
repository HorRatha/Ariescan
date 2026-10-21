# Installation Guide

## Prerequisites

- **Node.js** 16+ or **Python** 3.8+
- **npm** or **yarn** (for Node projects)
- **Git** (for cloning the repository)
- **Docker & Docker Compose** (optional, for containerized setup)

---

## Option 1: Manual Setup (Local Development)

### 1. Clone the Repository

```bash
git clone https://github.com/HorRatha/Ariescan.git
cd Ariescan
```

### 2. Setup Backend

```bash
cd backend

# Install dependencies
npm install

# Create .env file
cp .env.example .env

# Start backend server
npm start
```

The backend will be available at: `http://localhost:5000`

### 3. Setup Frontend

In a new terminal:

```bash
cd frontend

# Install dependencies
npm install

# Create .env file
cp .env.example .env

# Start frontend development server
npm start
```

The frontend will be available at: `http://localhost:3000`

---

## Option 2: Docker Setup

### Prerequisites
- Docker installed
- Docker Compose installed

### Quick Start

```bash
# From the Ariescan root directory
docker-compose -f docker/docker-compose.yml up --build
```

Services will be available at:
- **Frontend**: http://localhost:3000
- **Backend**: http://localhost:5000

### Stop Services

```bash
docker-compose -f docker/docker-compose.yml down
```

### View Logs

```bash
docker-compose -f docker/docker-compose.yml logs -f backend
docker-compose -f docker/docker-compose.yml logs -f frontend
```

---

## Option 3: Production Deployment

### Docker Image Build

```bash
# Backend
cd backend
docker build -t ariescan-backend:1.0 .

# Frontend
cd frontend
docker build -t ariescan-frontend:1.0 .
```

### Push to Registry

```bash
docker tag ariescan-backend:1.0 your-registry/ariescan-backend:1.0
docker push your-registry/ariescan-backend:1.0

docker tag ariescan-frontend:1.0 your-registry/ariescan-frontend:1.0
docker push your-registry/ariescan-frontend:1.0
```

---

## Troubleshooting

### Backend fails to start

```bash
# Check Node version
node --version  # Should be 16+

# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Check if port 5000 is in use
netstat -an | grep 5000
```

### Frontend won't connect to backend

1. Verify backend is running: `curl http://localhost:5000/health`
2. Check `.env` file has correct `REACT_APP_API_URL`
3. Check browser console for CORS errors
4. Restart frontend development server

### Docker issues

```bash
# Clean up all containers and images
docker system prune -a

# Rebuild from scratch
docker-compose -f docker/docker-compose.yml up --build --force-recreate
```

---

## Next Steps

- Read [API Documentation](./API.md)
- Check [Usage Guide](./USAGE.md)
- See [Contributing Guidelines](./CONTRIBUTING.md)
