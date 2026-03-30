# ── Production build ──────────────────────────────
FROM node:20-alpine AS production

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm ci

COPY . .
RUN npm run build

EXPOSE 3000

CMD ["npm", "start"]

# ── Development build (hot-reload) ───────────────
FROM node:20-alpine AS development

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm install

# Source mounted as volume for hot-reload
EXPOSE 3000

CMD ["npm", "run", "dev"]
