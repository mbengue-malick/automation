FROM node:lts-alpine

WORKDIR /app

COPY . .

RUN npm ci \
  --prefer-offline \
  --pure-lockfile \
  --non-interactive

RUN npm run build

EXPOSE 3000

CMD ["npm", "run", "serve", "--", "--port", "3000", "--host", "0.0.0.0"]
