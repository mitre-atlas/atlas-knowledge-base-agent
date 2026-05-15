FROM artifacts.mitre.org:8200/langflowai/langflow:1.9.2 

ENV DEBIAN_FRONTEND=noninteractive

USER root

RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
    jq && \
    curl -L -o /usr/local/share/ca-certificates/MITRE-BA-NPE-CA-3-1.crt "http://pki.mitre.org/MITRE%20BA%20NPE%20CA-3(1).crt" && \
    curl -L -o /usr/local/share/ca-certificates/MITRE-BA-ROOT.crt "http://pki.mitre.org/MITRE%20BA%20ROOT.crt" && \
    curl -L -o /usr/local/share/ca-certificates/MITRE-NPE-CA1.crt "http://pki.mitre.org/MITRE-NPE-CA1.crt" && \
    curl -L -o /usr/local/share/ca-certificates/ZScaler_Root.crt "http://pki.mitre.org/ZScaler_Root.crt" && \
    update-ca-certificates

ENV AWS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
ENV CURL_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
ENV NODE_EXTRA_CA_CERTS=/etc/ssl/certs/ca-certificates.crt
ENV REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
ENV SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt

USER user

# Create folders and set the working directory
RUN mkdir /app/.langflow
RUN mkdir /app/flows
# RUN mkdir /app/components/
WORKDIR /app

# Copy flows and components to the container
COPY flows /app/flows


# Optional: Use custom dependencies
COPY pyproject.toml uv.lock /app/

EXPOSE 7860

# CMD ["langflow", "run", "--backend-only", "--host", "0.0.0.0", "--port", "7860"]
CMD ["langflow", "run", "--host", "0.0.0.0", "--port", "7860"]
