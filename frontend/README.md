# Ariescan Frontend

Modern Next.js dashboard for Ariescan API testing platform.

## Stack

- **Next.js 16** - React framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **Node.js 18+** - Runtime

## Setup

### Development

```bash
npm install
npm run dev
```

Access at: http://localhost:3000

### Build

```bash
npm run build
npm start
```

### Linting

```bash
npm run lint
npm run type-check
```

## Project Structure

```
src/
├── app/                    # Next.js app directory
│   ├── layout.tsx         # Root layout
│   ├── page.tsx           # Home page
│   └── globals.css        # Global styles + Tailwind
├── components/            # Reusable components
│   ├── Button.tsx
│   ├── Card.tsx
│   └── index.ts
└── lib/                   # Utilities
    └── env.ts
```

## Environment Variables

Create `.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:5000
NEXT_PUBLIC_API_TIMEOUT=30000
NEXT_PUBLIC_ENV=development
```

## Features

- ✅ TypeScript support
- ✅ Tailwind CSS styling
- ✅ Responsive design
- ✅ Component library
- ✅ Docker ready
- ✅ Production optimized

## Commands

| Command | Description |
|---------|-------------|
| `npm run dev` | Start dev server |
| `npm run build` | Build for production |
| `npm start` | Start production server |
| `npm run lint` | Run ESLint |
| `npm run type-check` | Check TypeScript |

## Docker

```bash
docker build -t ariescan-frontend:1.0 .
docker run -p 3000:3000 ariescan-frontend:1.0
```

## Contributing

See [CONTRIBUTING.md](../docs/CONTRIBUTING.md)
