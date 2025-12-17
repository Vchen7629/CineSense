# build stage
FROM node:23-alpine AS build

WORKDIR /app

COPY package*.json ./

RUN npm ci

COPY . .

ARG VITE_API_BASE_URL
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

RUN npm run build

#Server
FROM nginx:alpine

# Copy built assets to nginx html directory
COPY --from=build /app/dist /usr/share/nginx/html

#  custom nginx config for SPA routing
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "g", "daemon off;"]