FROM node:20-bookworm

# Build tools + zsign dependencies
RUN apt-get update && apt-get install -y \
    git g++ make pkg-config libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Build zsign from source (official Linux build: make in build/linux)
RUN git clone https://github.com/zhlynn/zsign.git /tmp/zsign \
    && cd /tmp/zsign/build/linux \
    && make clean && make \
    && BIN="$(find /tmp/zsign -type f -name zsign -perm -u+x | head -n 1)" \
    && test -n "$BIN" \
    && cp "$BIN" /usr/local/bin/zsign \
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
