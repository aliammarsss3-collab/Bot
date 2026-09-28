FROM node:20-bookworm

# Build tools + zsign dependencies
RUN apt-get update && apt-get install -y \
    git cmake build-essential libssl-dev zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Build zsign from source
RUN git clone https://github.com/zhlynn/zsign.git /tmp/zsign \
    && cd /tmp/zsign/build/linux \
    && ./build.sh \
    && cp zsign /usr/local/bin/zsign \
    && rm -rf /tmp/zsign

WORKDIR /app
COPY package.json ./
RUN npm install --omit=dev
COPY . .

# Runtime data (db, IPAs, certs) goes to /data — mount a Railway Volume there so it survives redeploys
ENV DATA_DIR=/data
RUN mkdir -p /data

EXPOSE 3000
CMD ["node", "server.js"]
