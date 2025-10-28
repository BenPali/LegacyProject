FROM python:3.11-slim

LABEL maintainer="BenPali"
LABEL description="LegacyProject for GeneWeb"

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    make \
    && rm -rf /var/lib/apt/lists/*

COPY modernProject/ /app/modernProject/
COPY Makefile /app/

RUN pip install --no-cache-dir pytest pytest-cov

RUN useradd -m -u 1000 geneweb && \
    chown -R geneweb:geneweb /app

USER geneweb

EXPOSE 2317

ENV PYTHONPATH=/app/modernProject
ENV PYTHONUNBUFFERED=1

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import socket; s=socket.socket(); s.connect(('127.0.0.1', 2317)); s.close()" || exit 1

WORKDIR /app/modernProject

VOLUME /data

CMD ["python", "-m", "bin.gwd", "-p", "2317", "-wd", "/data", "-addr", "0.0.0.0"]
