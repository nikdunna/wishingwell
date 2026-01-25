# WishingWell Implementation Plan

## Current State (as of 2026-01-24)

### Backend (be/)
- Python 3.12 with basic LDA topic modeling (`topicmodeling.py`)
- Pipfile with: nltk, gensim, pyldavis
- **Missing**: FastAPI, PostgreSQL, all API structure

### Frontend (fe/)
- Next.js 16.1.2 + React 19.2.3 + TypeScript + Tailwind CSS v4
- Empty home page (`app/page.tsx`), basic layout
- **Missing**: All UI components, API client, pages

### What's Missing
- PostgreSQL database setup
- FastAPI backend application
- All API endpoints (wishes, topics, admin, visualization)
- Content moderation service
- BERTopic pipeline (replacing LDA)
- OpenAI labeling service
- Scheduler for batch updates
- All frontend components and pages

---

## Implementation Phases

### Phase 1: Backend Foundation (be/)
**Status**: `TODO`

- [ ] Create FastAPI application (`main.py`)
- [ ] Set up PostgreSQL with migrations (`migrations/001_initial_schema.sql`)
- [ ] Create SQLAlchemy models:
  - [ ] `models/wish.py`
  - [ ] `models/topic.py`
  - [ ] `models/model_update.py`
  - [ ] `models/rejected_wish.py`
- [ ] Implement base API router structure (`routers/`)
- [ ] Add CORS, environment config, logging

### Phase 2: Core Wish API
**Status**: `TODO`

- [ ] Create `services/content_moderation.py` - OpenAI-based moderation
- [ ] Implement POST /wishes (submit with validation + moderation check)
- [ ] Implement GET /wishes (pagination, filtering)
- [ ] Implement GET /wishes/:id (single wish + related)

### Phase 3: BERTopic Pipeline
**Status**: `TODO`

- [ ] Create `services/topic_modeling.py` - BERTopic wrapper
  - Embedding: all-MiniLM-L6-v2 (sentence-transformers)
  - Dimensionality reduction: UMAP (n_components=5)
  - Clustering: HDBSCAN (min_cluster_size=10)
- [ ] Create `services/openai_labeling.py` - GPT-4o-mini label generation
- [ ] Create `services/scheduler.py` - Background batch updates
- [ ] Implement GET /topics and GET /topics/:id/wishes
- [ ] Implement POST /admin/model/train

### Phase 4: Frontend (fe/)
**Status**: `TODO`

- [ ] Create `lib/types.ts` - TypeScript interfaces
- [ ] Create `lib/api.ts` - API client with fetch
- [ ] Implement `components/WishForm.tsx` - Submission form
- [ ] Implement `components/WishList.tsx` - Paginated list
- [ ] Implement `components/TopicCloud.tsx` - 2D visualization with D3.js
- [ ] Create pages:
  - [ ] `app/submit/page.tsx`
  - [ ] `app/topics/page.tsx`
  - [ ] `app/topics/[id]/page.tsx`
  - [ ] `app/wish/[id]/page.tsx`
- [ ] Update `app/page.tsx` - Home with recent wishes

### Phase 5: Polish & Integration
**Status**: `TODO`

- [ ] Add loading states, error handling
- [ ] Implement infinite scroll
- [ ] Add responsive design
- [ ] Replace pyLDAvis with custom D3.js visualization
- [ ] Set up database indexes for performance

---

## Database Schema

### Tables to Create

1. **wishes** - Core wish storage
   - `id` (UUID, PK)
   - `content` (TEXT, NOT NULL)
   - `created_at`, `updated_at` (TIMESTAMP)
   - `topic_id` (FK → topics.id, nullable)
   - `is_deleted` (BOOLEAN)

2. **topics** - Topic metadata
   - `id` (SERIAL, PK)
   - `name` (VARCHAR 255, from OpenAI)
   - `description` (TEXT)
   - `wish_count` (INTEGER, indexed)
   - `embedding_model` (VARCHAR)
   - `topic_model_id` (VARCHAR, for version tracking)

3. **rejected_wishes** - Content moderation log
   - `id` (UUID, PK)
   - `content` (TEXT, original wish)
   - `rejection_reason` (VARCHAR)
   - `moderation_model` (VARCHAR)
   - `created_at` (TIMESTAMP)

4. **topic_wishes** - Many-to-many with probabilities
   - `topic_id`, `wish_id` (FKs)
   - `probability` (DECIMAL 5,4)
   - `is_primary` (BOOLEAN)

5. **model_updates** - Training history
   - `version` (INTEGER, auto-incrementing)
   - `status` (running/completed/failed)
   - `wishes_count`, `topics_created`
   - `started_at`, `completed_at`
   - `configuration` (JSONB)

---

## API Endpoints

Base URL: `http://localhost:8000/api/v1`

### Wishes
- `POST /wishes` - Submit wish
- `GET /wishes?page=1&limit=20&sort=recent` - List with pagination
- `GET /wishes/:id` - Single wish with related wishes

### Topics
- `GET /topics?sort=popular` - List all topics
- `GET /topics/:id` - Topic details
- `GET /topics/:id/wishes` - Wishes for a topic

### Visualization
- `GET /visualization/topics` - 2D projection data
- `GET /visualization/topics/:id/words` - Top words with c-TF-IDF scores

### Admin
- `POST /admin/model/train` - Trigger BERTopic training
- `GET /admin/model/status` - Training status
- `GET /admin/model/history` - Training history

---

## Dependencies to Add

### Backend (Pipfile)
```
fastapi, uvicorn, pydantic, sqlalchemy, psycopg2-binary, alembic
bertopic, sentence-transformers, umap-learn, hdbscan, scikit-learn
openai, apscheduler, python-dotenv
```

### Frontend (package.json)
```
@tanstack/react-query, d3, @types/d3
react-hook-form, zod
date-fns
```

---

## Critical Files to Create

### Backend (be/)
- `main.py` - FastAPI app
- `database.py` - PostgreSQL connection
- `models/` - SQLAlchemy models
- `routers/` - API routers
- `services/topic_modeling.py` - BERTopic service
- `services/openai_labeling.py` - Label generation
- `services/content_moderation.py` - Content moderation
- `services/scheduler.py` - Background updates
- `config.py` - Environment config
- `migrations/001_initial_schema.sql` - Database schema

### Frontend (fe/)
- `lib/types.ts` - TypeScript interfaces
- `lib/api.ts` - API client
- `components/` - UI components
- `app/submit/page.tsx`
- `app/topics/page.tsx`
- `app/topics/[id]/page.tsx`
- `app/wish/[id]/page.tsx`

---

## Verification Plan

### Backend
- [ ] PostgreSQL schema created with all tables and indexes
- [ ] POST /wishes rejects inappropriate content and stores valid wishes
- [ ] GET /wishes returns paginated list
- [ ] BERTopic trains on sample data and creates topics
- [ ] OpenAI generates human-readable labels
- [ ] Content moderation blocks harmful wishes
- [ ] Scheduler triggers batch updates automatically

### Frontend
- [ ] Wish form submits and redirects to wish detail
- [ ] Wish list displays with pagination
- [ ] Topic visualization renders interactively
- [ ] Topic filtering works correctly
- [ ] Responsive design on mobile

### End-to-End
- [ ] Submit wish → stored in DB → batch update → topic assigned → visible in UI
- [ ] Topic cloud shows correct clusters and sizes
- [ ] Related wishes are semantically similar
