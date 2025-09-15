#!/bin/bash

# BirdBrain Lite - 90 Second Demo Script
# This script demonstrates the key features of the adaptive learning system

echo "BirdBrain Lite - 90 Second Demo"
echo "================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_step() {
    echo -e "${BLUE}[STEP $1]${NC} $2"
}

print_success() {
    echo -e "${GREEN}[SUCCESS] $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}[WARNING] $1${NC}"
}

print_error() {
    echo -e "${RED}[ERROR] $1${NC}"
}

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker and try again."
    exit 1
fi

print_step "1" "Starting BirdBrain Lite application..."
echo "   This will start both backend and frontend services"
echo ""

# Start the application
docker-compose up --build -d

# Wait for services to be ready
print_step "2" "Waiting for services to start..."
sleep 10

# Check if backend is healthy
print_step "3" "Checking backend health..."
if curl -s http://localhost:8000/health > /dev/null; then
    print_success "Backend is running at http://localhost:8000"
else
    print_error "Backend failed to start. Check logs with: docker-compose logs backend"
    exit 1
fi

# Check if frontend is accessible
print_step "4" "Checking frontend accessibility..."
if curl -s http://localhost:5173 > /dev/null; then
    print_success "Frontend is running at http://localhost:5173"
else
    print_warning "Frontend might still be starting. Check http://localhost:5173 in your browser"
fi

echo ""
print_step "5" "DEMO INSTRUCTIONS"
echo "   Open your browser and go to: http://localhost:5173"
echo ""
echo "   Follow these steps to see the adaptive learning in action:"
echo ""
echo "   1. Click 'Get Next Exercise' to start"
echo "   2. Answer quickly (< 2 seconds) - watch mastery increase"
echo "   3. Answer slowly (> 6 seconds) - notice different mastery update"
echo "   4. Answer incorrectly - see how it affects difficulty selection"
echo "   5. Watch the mastery bars change in real-time"
echo "   6. Read the explanations for why each exercise was chosen"
echo "   7. Try the 'Reset Session' button to start over"
echo ""

print_step "6" "KEY FEATURES TO OBSERVE"
echo "   • Mastery bars update differently based on response time"
echo "   • Exercise difficulty adapts to your performance"
echo "   • System explains why it chose each exercise"
echo "   • Streak counters track consecutive correct answers"
echo "   • Latency affects learning updates (fast vs slow responses)"
echo ""

print_step "7" "API DOCUMENTATION"
echo "   Backend API docs: http://localhost:8000/docs"
echo "   Interactive API explorer: http://localhost:8000/redoc"
echo ""

print_step "8" "TESTING THE SYSTEM"
echo "   Run the test suite:"
echo "   make test"
echo ""
echo "   Or test individual components:"
echo "   cd backend && python -m pytest tests/ -v"
echo ""

print_step "9" "STOPPING THE DEMO"
echo "   To stop the application:"
echo "   make docker-down"
echo "   or"
echo "   docker-compose down"
echo ""

print_success "Demo setup complete! The application is ready to use."
echo ""
echo "Quick Test Commands:"
echo "   # Test API directly"
echo "   curl http://localhost:8000/health"
echo "   curl -X POST http://localhost:8000/next"
echo ""
echo "   # View logs"
echo "   docker-compose logs -f"
echo ""
echo "   # Stop everything"
echo "   docker-compose down"
echo ""

print_warning "Note: This demo uses in-memory storage, so data resets when you stop the application."
echo ""

echo "Happy Learning with BirdBrain Lite!"
