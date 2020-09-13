FROM node:14

# install dependencies
COPY package.json package-lock.json /app/
WORKDIR /app

ENV PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true \
	CHROMIUM_PATH=/usr/bin/chromium
RUN set -x && \
	apt-get update && \
	apt-get install -y chromium && \
	npm install && \
	rm -rf /var/lib/apt/lists/*

# add the actual app
ADD server.js /app/

USER 1000:1000
ENV BIND_ADDR=0.0.0.0 PORT=1337
CMD ["npm", "start"]
