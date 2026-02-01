# Deploying Wishing Well Backend to Railway

## Quick Start

### 1. Install Railway CLI

```bash
npm install -g @railway/cli
```

### 2. Login to Railway

```bash
railway login
```

### 3. Initialize Railway Project

```bash
cd /Users/ndunna/dev/mvps/wishingwell/be
railway init
```

This creates a new Railway project linked to this directory.

### 4. Add PostgreSQL Database

```bash
railway add postgresql
```

Railway will create a PostgreSQL database and set the `DATABASE_URL` environment variable automatically.

### 5. Set Environment Variables

```bash
railway variables set OPENAI_API_KEY=sk-your-key-here
railway variables set OPENAI_MODEL=gpt-4o-mini
railway variables set EMBEDDING_MODEL=all-MiniLM-L6-v2
railway variables set UMAP_N_COMPONENTS=5
railway variables set HDBSCAN_MIN_CLUSTER_SIZE=10
railway variables set MIN_TOPIC_SIZE=5
railway variables set BATCH_UPDATE_INTERVAL_MINUTES=60
railway variables set ENABLE_SCHEDULER=false
railway variables set CORS_ORIGINS=https://your-frontend-domain.vercel.app
```

### 6. Run Database Migrations

Get the database connection string:

```bash
railway variables get DATABASE_URL
```

Then connect and run migrations:

```bash
# Get the database URL (will be in format: postgresql://...)
# Use psql or any PostgreSQL client to run:

psql $DATABASE_URL -f migrations/001_initial_schema.sql
```

Or use Railway's PostgreSQL console in the dashboard.

### 7. Deploy

```bash
railway up
```

This builds the Docker image and deploys to Railway.

### 8. Get Your API URL

```bash
railway domain
```

This will show you your deployed API URL (e.g., `https://wishingwell-backend.up.railway.app`).

### 9. Update Frontend CORS

Add your Railway backend URL to the frontend's CORS settings:

```bash
# In Railway backend variables
railway variables set CORS_ORIGINS=https://your-frontend.vercel.app,https://localhost:3000
```

## Environment Variables Reference

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection (auto-set by Railway) | `postgresql://postgres:...` |
| `OPENAI_API_KEY` | Your OpenAI API key | `sk-proj-...` |
| `OPENAI_MODEL` | Model for topic labeling | `gpt-4o-mini` |
| `EMBEDDING_MODEL` | Sentence transformer model | `all-MiniLM-L6-v2` |
| `UMAP_N_COMPONENTS` | UMAP components | `5` |
| `HDBSCAN_MIN_CLUSTER_SIZE` | Minimum cluster size | `10` |
| `MIN_TOPIC_SIZE` | Minimum topic size | `5` |
| `BATCH_UPDATE_INTERVAL_MINUTES` | Scheduler interval | `60` |
| `ENABLE_SCHEDULER` | Enable background scheduler | `false` |
| `CORS_ORIGINS` | Allowed frontend origins | `https://your-app.vercel.app` |
| `DEFAULT_PAGE_SIZE` | Pagination size | `20` |
| `MAX_PAGE_SIZE` | Max pagination size | `100` |

## Monitoring

### View Logs

```bash
railway logs
```

### View Status

```bash
railway status
```

### Open Dashboard

```bash
railway open
```

## Database Access

### Via Railway CLI

```bash
railway connect
```

### Via psql

```bash
# Get DATABASE_URL
railway variables get DATABASE_URL

# Connect
psql $(railway variables get DATABASE_URL)
```

## Troubleshooting

### Build Failures

If the build fails, check:
1. All dependencies in `Pipfile` are valid
2. No syntax errors in Python files
3. Dockerfile is in the root directory

### Runtime Errors

Check logs with `railway logs` and verify:
1. Environment variables are set correctly
2. Database migrations have been run
3. OpenAI API key is valid

### Database Connection Issues

1. Verify DATABASE_URL is set: `railway variables get DATABASE_URL`
2. Check database is running in Railway dashboard
3. Ensure migrations were applied

### Scheduler Not Running

The scheduler is disabled by default (`ENABLE_SCHEDULER=false`). To enable:

```bash
railway variables set ENABLE_SCHEDULER=true
railway up
```

Note: Railway's restart policy means the scheduler will reset on redeploy.

## Production Considerations

1. **Enable Scheduler**: Set `ENABLE_SCHEDULER=true` for automatic topic updates
2. **Increase Cluster Size**: With more data, increase `HDBSCAN_MIN_CLUSTER_SIZE`
3. **Monitor Costs**: Railway charges for CPU/memory usage
4. **Set Up Alerts**: Configure Railway alerts for failures
5. **Database Backups**: Enable automatic backups in Railway dashboard

## Next Steps

After deploying the backend:
1. Deploy the frontend to Vercel
2. Update frontend `NEXT_PUBLIC_API_URL` to point to your Railway backend
3. Test the full integration
4. Enable the scheduler for automatic topic updates

## Cost Estimate

Railway pricing (as of 2024):
- **Free tier**: $5/month credit one-time
- **Basic**: ~$5-10/month for small apps
- **Database**: Included in base pricing
- **Estimated total**: $5-15/month for MVP

See https://railway.app/pricing for current pricing.
