FROM node:20-slim

ENV NODE_ENV=production \
    PORT=8787

WORKDIR /app/backend/gateway-node

COPY backend/gateway-node/package*.json ./
RUN npm ci --omit=dev

COPY backend/gateway-node/ ./
COPY widget/ /app/widget/

EXPOSE 8787

CMD ["node", "server.js"]