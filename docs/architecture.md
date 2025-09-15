# BirdBrain Lite - Architecture Diagrams

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        BirdBrain Lite                          │
├─────────────────────────────────────────────────────────────────┤
│  Frontend (React)          │  Backend (FastAPI)               │
│  ┌─────────────────────┐   │  ┌─────────────────────────────┐  │
│  │ • Exercise UI       │   │  │ • REST API Endpoints       │  │
│  │ • Mastery Tracking  │◄──┼──┤ • CORS Middleware          │  │
│  │ • Answer Input      │   │  │ • Request Validation       │  │
│  │ • Real-time Updates │   │  │ • Error Handling           │  │
│  └─────────────────────┘   │  └─────────────────────────────┘  │
│                             │  ┌─────────────────────────────┐  │
│                             │  │ • BKT Algorithm            │  │
│                             │  │ • Mastery Calculation      │  │
│                             │  │ • Latency Adjustment       │  │
│                             │  │ • Exercise Selection       │  │
│                             │  └─────────────────────────────┘  │
│                             │  ┌─────────────────────────────┐  │
│                             │  │ • In-Memory Store          │  │
│                             │  │ • Session State            │  │
│                             │  │ • Exercise Data            │  │
│                             │  └─────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Learning Flow

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Start     │───►│  Get Next   │───►│  Answer     │───►│  Measure    │
│  Session    │    │  Exercise   │    │  Question   │    │  Latency    │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
                                                              │
┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  Select     │◄───│  Calculate  │◄───│  Update     │◄────────┘
│  Next       │    │  Mastery    │    │  BKT Model  │
│  Exercise   │    │  Level      │    │            │
└─────────────┘    └─────────────┘    └─────────────┘
```

## BKT Algorithm Flow

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Current   │    │   Answer    │    │  Latency    │
│  Mastery    │    │ Correctness │    │  Analysis   │
│   Level     │    │             │    │             │
└─────────────┘    └─────────────┘    └─────────────┘
       │                   │                   │
       └───────────────────┼───────────────────┘
                           │
                    ┌─────────────┐
                    │  Adjusted    │
                    │ Correctness  │
                    │              │
                    │ • Fast + Correct = 1.0
                    │ • Slow + Correct = 0.75
                    │ • Fast + Wrong = 0.25
                    │ • Slow + Wrong = 0.0
                    └─────────────┘
                           │
                    ┌─────────────┐
                    │  Bayesian    │
                    │  Update      │
                    │              │
                    │ P(known) = f(P_old, correct, params)
                    └─────────────┘
                           │
                    ┌─────────────┐
                    │  New Mastery │
                    │  Level       │
                    └─────────────┘
```

## Exercise Selection Logic

```
┌─────────────┐
│  All Skills │
│  Mastery    │
│  Levels     │
└─────────────┘
       │
       ▼
┌─────────────┐
│  Find Skill │
│  with       │
│  Lowest     │
│  Mastery    │
└─────────────┘
       │
       ▼
┌─────────────┐
│  Determine  │
│  Difficulty │
│             │
│ • < 35% → Easy
│ • 35-70% → Medium
│ • > 70% → Hard
└─────────────┘
       │
       ▼
┌─────────────┐
│  Check      │
│  Recent     │
│  Failures   │
│             │
│ • Last 2 wrong?
│ • Back off difficulty
└─────────────┘
       │
       ▼
┌─────────────┐
│  Select     │
│  Exercise   │
│  from       │
│  Pool       │
└─────────────┘
```

## Data Flow

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Frontend  │    │   Backend   │    │   BKT       │
│             │    │             │    │   Engine    │
│ • User      │───►│ • Validate  │───►│ • Calculate │
│   Input     │    │   Request   │    │   Mastery   │
│             │    │             │    │             │
│ • Display   │◄───│ • Process   │◄───│ • Select    │
│   Results   │    │   Response  │    │   Exercise  │
└─────────────┘    └─────────────┘    └─────────────┘
```

## Component Hierarchy

```
App
├── MasteryBar (skill, mastery, streak)
├── ExerciseCard (exercise, onSubmit, isSubmitting)
│   ├── Question Display
│   ├── Multiple Choice Options
│   └── Submit Button
├── Error Display
├── Loading States
└── Reset Session Button
```

## API Request Flow

```
Frontend Request
       │
       ▼
┌─────────────┐
│  CORS       │
│  Middleware │
└─────────────┘
       │
       ▼
┌─────────────┐
│  Route      │
│  Handler    │
└─────────────┘
       │
       ▼
┌─────────────┐
│  BKT        │
│  Processing │
└─────────────┘
       │
       ▼
┌─────────────┐
│  Response   │
│  Generation │
└─────────────┘
       │
       ▼
Frontend Response
```
