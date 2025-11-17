FROM ros:jazzy

ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /app

# Install dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    python3-venv \
    python3-dev \
    python3-pip \
    python3-setuptools \
    libpq-dev \
    postgresql-client \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python3 -m venv /opt/venv
ENV VIRTUAL_ENV=/opt/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Upgrade tools
RUN pip install --upgrade pip setuptools wheel

# Install Python dependencies
COPY vending_api/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy app
COPY vending_api/ /app/

# Expose port
EXPOSE 8000

# DATABASE_URL will come from docker-compose
ENV HOST=0.0.0.0
ENV PORT=8000

CMD ["bash", "-lc", "source /opt/ros/jazzy/setup.bash && source /opt/venv/bin/activate && python run_server.py"]
