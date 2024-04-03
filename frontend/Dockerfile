FROM node:13.12.0-alpine
WORKDIR /app

COPY package*.json ./

RUN npm ci

COPY . .
RUN npm run build
RUN npm install --global http-server

CMD ["npx", "-y", "http-server", "-p", "7000", "/app/build"]

