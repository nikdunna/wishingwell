# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Wishing Well** is a topic modeling platform that groups user-submitted wishes into semantic topics using machine learning. The project uses a monorepo architecture with separate frontend and backend components.

## Additional Rules
Always use Context7 MCP when I need library/API documentation, code generation, setup or configuration steps without me having to explicitly ask.

### Technology Stack

**Frontend (`/fe/`)**: Next.js 16.1.2 (App Router) + React 19.2.3 + TypeScript + Tailwind CSS v4
**Backend (`/be/`)**: Python 3.12 with ML libraries (NLTK, Gensim, BERTopic planned)

### Current Status

The project is in early development. See `IMPLEMENTATION_PLAN.md` for the complete roadmap.

- **Backend**: Proof-of-concept LDA topic modeling exists in `be/topicmodeling.py`. Missing: FastAPI app, PostgreSQL, all API endpoints, BERTopic pipeline.
- **Frontend**: Next.js scaffold with empty home page. Missing: All UI components, API integration, pages.

## Development Commands

### Backend (Python)

```bash
cd be
pipenv install                 # Install dependencies from Pipfile
pipenv run python topicmodeling.py  # Run current proof-of-concept
```

The backend uses **Pipenv** for dependency management with Python 3.12.

### Frontend (Next.js)

```bash
cd fe
npm install                    # Install dependencies
npm run dev                    # Start development server on localhost:3000
npm run build                  # Build for production
npm run lint                   # Run ESLint
npm run start                  # Start production server
```

The frontend uses **npm** and runs on port 3000 by default.

## Architecture

### Monorepo Structure

```
wishingwell/
├── be/           # Backend Python services
│   ├── Pipfile           # Python dependencies
│   └── topicmodeling.py  # Current LDA proof-of-concept
└── fe/           # Frontend Next.js app
    ├── app/             # Next.js App Router pages
    ├── public/          # Static assets
    └── package.json     # Node dependencies
```

### Planned Architecture

The full implementation (per `IMPLEMENTATION_PLAN.md`) includes:

**Backend Services**:
- FastAPI application with RESTful API
- PostgreSQL database with SQLAlchemy ORM
- BERTopic for topic modeling (replacing current LDA)
- OpenAI integration for content moderation and topic labeling
- APScheduler for batch topic updates
- pyLDAvis/D3.js for visualization

**Database Schema** (PostgreSQL):
- `wishes` - User-submitted wishes (UUID PK)
- `topics` - ML-generated topics with OpenAI labels
- `topic_wishes` - Many-to-many with probabilities
- `rejected_wishes` - Content moderation log
- `model_updates` - Training history

**API Endpoints** (Base: `http://localhost:8000/api/v1`):
- `POST /wishes` - Submit wish (with moderation check)
- `GET /wishes` - List wishes (paginated)
- `GET /wishes/:id` - Single wish with related wishes
- `GET /topics` - List all topics
- `GET /topics/:id/wishes` - Wishes for a topic
- `GET /visualization/topics` - 2D projection data
- `POST /admin/model/train` - Trigger BERTopic training

### Frontend Architecture (Planned)

- **App Router**: File-based routing in `fe/app/`
- **TypeScript Path Alias**: `@/*` maps to `fe/` root
- **Styling**: Tailwind CSS v4 with PostCSS
- **State Management**: TanStack Query planned
- **Visualization**: D3.js for interactive topic exploration

## Key Implementation Details

### Backend ML Pipeline

The current proof-of-concept (`be/topicmodeling.py`) demonstrates:
1. Text preprocessing with NLTK (stopwords, lemmatization)
2. LDA topic modeling with Gensim
3. pyLDAvis visualization (outputs to `lda_visualization.html`)

The production version will use **BERTopic** with:
- Embeddings: `all-MiniLM-L6-v2` (sentence-transformers)
- Dimensionality reduction: UMAP (n_components=5)
- Clustering: HDBSCAN (min_cluster_size=10)
- Labeling: GPT-4o-mini via OpenAI API

### Content Moderation

Planned OpenAI integration to filter inappropriate wishes before storage and topic modeling.

### Topic Model Updates

Background scheduler (APScheduler) will:
1. Batch unassigned wishes
2. Run BERTopic training
3. Generate labels via OpenAI
4. Update database with new topic assignments

## File Organization Patterns

### Backend (Planned)

```
be/
├── main.py                  # FastAPI application entry point
├── database.py              # PostgreSQL connection
├── config.py                # Environment configuration
├── models/                  # SQLAlchemy models
│   ├── wish.py
│   ├── topic.py
│   └── model_update.py
├── routers/                 # API route handlers
│   ├── wishes.py
│   ├── topics.py
│   └── admin.py
├── services/                # Business logic
│   ├── topic_modeling.py    # BERTopic wrapper
│   ├── openai_labeling.py   # GPT-4o-mini label generation
│   ├── content_moderation.py # OpenAI moderation
│   └── scheduler.py         # Background jobs
└── migrations/              # Database migrations
    └── 001_initial_schema.sql
```

### Frontend (Planned)

```
fe/
├── app/                     # Next.js App Router
│   ├── page.tsx            # Home (recent wishes)
│   ├── submit/page.tsx     # Wish submission form
│   ├── topics/page.tsx     # Topic listing
│   ├── topics/[id]/page.tsx # Topic detail
│   └── wish/[id]/page.tsx  # Wish detail
├── components/              # React components
│   ├── WishForm.tsx
│   ├── WishList.tsx
│   └── TopicCloud.tsx      # D3.js visualization
└── lib/                     # Utilities
    ├── types.ts            # TypeScript interfaces
    └── api.ts              # API client (fetch)
```

## Development Workflow Notes

### Testing the ML Pipeline

To test the current LDA implementation:
```bash
cd be
pipenv run python topicmodeling.py
# Opens lda_visualization.html in browser
```

To test BERTopic (once implemented):
```bash
cd be
pipenv shell
python -c "from services.topic_modeling import train_model; train_model()"
```

### Database Migrations

The project will use SQL migrations (not Alembic). Run migrations directly:
```bash
cd be
psql -U postgres -d wishingwell -f migrations/001_initial_schema.sql
```

### Environment Variables

Create `.env` files in both `be/` and `fe/`:

**Backend** (`be/.env`):
```
DATABASE_URL=postgresql://user:pass@localhost:5432/wishingwell
OPENAI_API_KEY=sk-...
```

**Frontend** (`fe/.env`):
```
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

## Important Context

### Why BERTopic over LDA?

The current proof-of-concept uses LSA/LDA for simplicity. The production version uses BERTopic because:
1. Better semantic understanding (transformer embeddings vs. bag-of-words)
2. Handles short text better (wishes are typically 1-2 sentences)
3. Dynamic topic discovery (no fixed number of topics)
4. State-of-the-art clustering (HDBSCAN)

### OpenAI Integration

Two separate OpenAI integrations:
1. **Content Moderation**: Filter wishes before storage (uses moderation endpoint)
2. **Topic Labeling**: Generate human-readable labels for topics (uses GPT-4o-mini)

### Visualization Strategy

pyLDAvis is used for current LDA proof-of-concept. Production will use custom D3.js visualization for better UX and real-time interactivity with the frontend.

## TypeScript Configuration

- Path alias `@/*` maps to `fe/` root
- Strict mode enabled
- Target: ES2017
- Module resolution: bundler (Next.js optimizes)

## Tailwind CSS v4

Uses the new Tailwind CSS v4 with PostCSS plugin. Configuration in `fe/postcss.config.mjs`. No `tailwind.config.js` file - v4 uses CSS-based configuration.

## Git Status Notes

- Modified files: `be/Pipfile`, `be/Pipfile.lock`, `be/topicmodeling.py`
- Untracked: `IMPLEMENTATION_PLAN.md`, `be/lda_visualization.html`
- Recent work focused on ML proof-of-concept
