# Insurance Claims Processing Platform - Backend Engineering Challenge

## Overview

Design and implement a backend system for an agentic insurance claims processing platform. This challenge is about building a system from the ground up with appropriate structure while giving you freedom in implementation details. Be creative and have fun!


## Business Context

Strala is building an AI-driven claims processing platform for property & casualty insurance. The key innovation is an agentic workflow system where:

1. AI models analyze claims data and generate suggestions/actions
2. Human adjusters review these suggestions and accept/reject them
3. The system learns from this feedback to improve future recommendations

## Project Structure

We've provided a minimal structure with example data models and route stubs:

```
claims-api/
├── app/
│   ├── models/
│   │   ├── enums.py         # Status enums
│   │   ├── types.py         # Type definitions
│   │   └── schemas.py       # Data models
│   └── api/
│       └── routes/
│           ├── claims.py     # Example route stubs
│           └── suggestions.py # Example route stubs
├── README.md                 # Assignment instructions
```

These files contain example data structures and route stubs to get you started, but they're intentionally incomplete. You should:

- Expand upon these examples or create your own
- Choose your own frameworks, programming languages, and tools
- Implement some of the actual functionality
- Add appropriate testing, documentation, and infrastructure

## Core Requirements

Build a minimal but functional backend API that demonstrates:

### 1. Agentic Workflow
- Design a system where AI agents can suggest actions on insurance claims
- Implement endpoints for human reviewers to accept/reject these suggestions
- Track the feedback loop between AI suggestions and human decisions
- You don't have to implement AI models, but you should design endpoints for them

### 2. Claims Processing
- Support basic claim submission and retrieval
- Design your own data model based on the examples provided
- Suggest database schemas for the data model

### 3. Technical Implementation
- Choose your own tech stack (at the moment, we use Python/FastAPI/PostgreSQL, but use what you're comfortable with!)
- Set up your own project structure, dependencies, and environment
- Implement appropriate documentation and tests

## Model Examples

We've provided example data models in the `app/models/` directory:

- **enums.py**: Contains status enums for claims and suggestions
- **types.py**: Defines type aliases for improved readability
- **schemas.py**: Contains TypedDict definitions for core data structures

Feel free to use these as-is, modify them, or create your own models that better fit your implementation.

## API Examples

We've provided stub files for API routes in `app/api/routes/`:

- **claims.py**: Example endpoints for claim management
- **suggestions.py**: Example endpoints for AI suggestions and human feedback

These files contain commented pseudocode to give you an idea of the expected functionality. Implement them according to your chosen framework and architecture.

## Expected Endpoints

Your API should include endpoints similar to these (feel free to modify based on your implementation):

### Claims Management

- `POST /api/claims` - Submit a new claim
- `GET /api/claims/{claim_id}` - Get claim details
- `GET /api/claims` - List claims with filtering options
- `PATCH /api/claims/{claim_id}` - Update claim status or details

### AI Suggestion System

- `POST /api/claims/{claim_id}/suggestions` - Generate AI suggestions for a claim
- `GET /api/claims/{claim_id}/suggestions` - Get all suggestions for a claim
- `GET /api/suggestions/{suggestion_id}` - Get a specific suggestion

### Human Feedback Loop

- `POST /api/suggestions/{suggestion_id}/review` - Accept, reject, or modify a suggestion
- `GET /api/suggestions/metrics` - Get metrics on suggestion accuracy and acceptance rates

## Evaluation Criteria

We'll evaluate your submission based on:

1. **System architecture** - Overall design and component organization
2. **AI integration** - How you incorporate AI agents and handle their suggestions
3. **Human feedback loop** - Implementation of accept/reject mechanics and how they affect the system
4. **Code quality** - Structure, readability, and maintainability
5. **Documentation** - API documentation and explanation of your approach
6. **Testing** - Test coverage and methodology

## Submission Instructions

1. Create a GitHub repository with your implementation
2. Include a comprehensive README that explains:
   - Your system architecture and design decisions
   - How to set up and run your application
   - API documentation
   - How the AI-human feedback loop works in your implementation
   - What you would improve given more time
3. Share the repository link with us

Good luck! We're excited to see your creative approach to this problem.
