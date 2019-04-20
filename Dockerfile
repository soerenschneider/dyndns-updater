FROM python:3.7-alpine

COPY requirements.txt /opt/dyndns/requirements.txt
WORKDIR /opt/dyndns
RUN pip install --no-cache-dir -r requirements.txt

COPY ipv4_providers.py dns_client.py dyndns_updater.py /opt/dyndns/

RUN useradd toor
USER toor

CMD ["python3", "dns_client.py"]

