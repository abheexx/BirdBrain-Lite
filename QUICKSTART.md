# BirdBrain Lite - Quick Start Guide

## Get Started in 30 Seconds

```bash
# 1. Start the application
make docker-up

# 2. Open your browser
open http://localhost:5173

# 3. Click "Get Next Exercise" and start learning!
```

## What You'll See

- **Mastery Bars**: Real-time progress tracking for each skill
- **Adaptive Questions**: Difficulty adjusts based on your performance
- **Smart Explanations**: AI explains why it chose each exercise
- **Latency Awareness**: Response time affects learning updates

## Development Commands

```bash
# Start development mode
make dev

# Run tests
make test

# Format code
make format

# Stop everything
make docker-down
```

## Key Features

1. **Bayesian Knowledge Tracing**: Tracks your mastery of each skill
2. **Latency Adaptation**: Fast/slow responses affect learning differently
3. **Explainable AI**: Clear reasoning for exercise selection
4. **Real-time Updates**: Live mastery tracking and progress visualization

## Demo Workflow

1. Answer quickly (< 2 seconds) - watch mastery increase normally
2. Answer slowly (> 6 seconds) - notice different mastery update
3. Answer incorrectly - see how it affects difficulty selection
4. Watch mastery bars change in real-time
5. Read explanations for why each exercise was chosen

## Learn More

- Full documentation: [README.md](README.md)
- API docs: http://localhost:8000/docs
- Architecture diagrams: [docs/architecture.md](docs/architecture.md)
- Run demo script: `./demo.sh`
