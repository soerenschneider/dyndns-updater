FROM python:3.7-alpine

RUN RUN addgroup -S toor && adduser -S toor -G toor

COPY requirements.txt /opt/dyndns/requirements.txt
WORKDIR /opt/dyndns
RUN pip install --no-cache-dir -r requirements.txt

COPY ipv4_providers.py dns_client.py dyndns_updater.py /opt/dyndns/

USER toor
CMD ["python3", "dns_client.py"]

