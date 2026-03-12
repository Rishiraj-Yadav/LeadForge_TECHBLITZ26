# Deployment Notes

## Frontend on Vercel

1. Import the frontend directory or full repo into Vercel.
2. Set root directory to frontend if needed.
3. Add NEXT_PUBLIC_API_URL, NEXT_PUBLIC_SOCKET_URL, and Supabase public values.
4. Deploy.

## Backend on Railway

1. Create a Railway project.
2. Add backend service from the repo.
3. Set start command:
   uvicorn app.main:app --host 0.0.0.0 --port $PORT
4. Add Redis plugin or separate Redis service.
5. Add all backend environment variables.
6. Set public domain and update webhook callback URLs.

## Database on Supabase

1. Use Supabase managed Postgres.
2. Restrict service role key to backend only.
3. Add backups and RLS if you extend auth and multi-tenant storage.

## Monitoring

- Sentry for backend exceptions and frontend runtime errors.
- PostHog for product analytics.
- Better Stack for logs and uptime checks.
