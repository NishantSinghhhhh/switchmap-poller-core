# Use a lightweight Python base image
FROM python:3.11-slim

# Set up environment variables
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PATH="/opt/switchmap-poller/venv/bin:$PATH" \
    PYTHONPATH="/opt/switchmap-poller"

# Create a dedicated user for security
RUN groupadd -r switchmap && useradd --no-log-init -r -g switchmap switchmap

# Set working directory
WORKDIR /opt/switchmap-poller

# Install required dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    snmp \
    libsnmp-dev \
    snmp-mibs-downloader \
    net-tools \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

# Create a virtual environment
RUN python3 -m venv venv

# Copy dependency file separately for caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Ensure required directories exist
RUN mkdir -p /etc/switchmap-poller /var/log/switchmap-poller && \
    chmod -R 755 /var/log/switchmap-poller

# Copy configuration file
COPY examples/etc/config.yaml /etc/switchmap-poller/config.yaml

# Copy entrypoint script and set permissions
COPY entrypoint.sh /opt/switchmap-poller/entrypoint.sh
RUN chmod +x /opt/switchmap-poller/entrypoint.sh

# Switch to non-root user
USER switchmap

# Expose necessary ports
EXPOSE 7000 7001

# Start the service
CMD ["python", "-m", "switchmap.poller"]
