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
FROM node:23-alpine

WORKDIR /app

COPY --from=build /app/dist ./build

# non-root-user for security
USER node

EXPOSE 3000

RUN npm install -g serve

CMD ["serve", "-s", "build", "-l", "3000"]