# Vinmec Healthcare (Phase 1 - Step 1)

Next.js monolithic app bootstrap for Vinmec AI Assistant MVP.

## Tech stack

- Next.js App Router + TypeScript + Tailwind CSS
- Prisma + SQLite (schema initialized)

## Required structure

- `app/api/`: API route handlers
- `app/(routes)/`: app pages
- `components/`: reusable UI components
- `lib/server/`: server utilities and domain logic
- `lib/client/`: client-side fetch/API helpers
- `prisma/`: schema/migrations/seed
- `scripts/`: local utility scripts

## Environment

Copy `.env.example` to `.env` and adjust values:

```bash
cp .env.example .env
```

## Run locally

```bash
bun install
bun run dev
```

Open `http://localhost:3000`.

## Health endpoint

`GET /api/health` returns:

```json
{ "status": "ok", "ts": "2026-04-09T00:00:00.000Z" }
```

## Step 1 conventions

- Unified API error shape is defined in `lib/server/errors.ts`:
  - `code`
  - `message`
  - `details`
- Demo pages available:
  - `/`
  - `/demo`
