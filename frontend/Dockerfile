FROM node:20-alpine AS builder

WORKDIR /app

COPY package.json package-lock.json ./
ENV NEXT_TELEMETRY_DISABLED=1
RUN npm ci

COPY . .
ENV API_URL=http://api:8000
RUN npm run build

FROM node:20-alpine AS runner

WORKDIR /app

ENV NODE_ENV=production
ENV HOSTNAME=0.0.0.0
ENV PORT=3000
ENV API_URL=http://api:8000

COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static

EXPOSE 3000

CMD ["node", "server.js"]
