FROM python:3.14.0-slim-bookworm

EXPOSE 443
WORKDIR /app
COPY . .
RUN apt-get update
RUN apt-get install -y gcc
RUN pip install -r requirements.txt

# Install Playwright system dependencies and browsers
RUN apt-get install -y \
    libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 libcups2 \
    libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 \
    libxrandr2 libgbm1 libasound2 libpangocairo-1.0-0 libcairo2 \
    libxshmfence1 fonts-liberation libappindicator3-1 libgtk-3-0 \
    xvfb x11vnc fluxbox

# Install Playwright browsers
RUN playwright install --with-deps

# Set up display environment for headed mode
ENV DISPLAY=:99

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "443"]