FROM codercom/code-server:latest

USER root

# Install Python
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create venv and install AIPass
WORKDIR /app
COPY . .
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install -e .

# Switch back to coder user
USER coder

# venv on PATH for coder too
ENV PATH="/opt/venv/bin:$PATH"

EXPOSE 8080

ENTRYPOINT ["code-server", "--auth", "none", "--bind-addr", "0.0.0.0:8080", "/app"]
