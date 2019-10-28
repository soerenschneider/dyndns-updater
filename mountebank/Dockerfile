FROM registry.gitlab.com/soerenschneider/mountebank-docker
COPY dyndns.json /tmp/
EXPOSE 8080
CMD ["start", "--pidfile", "/tmp/mb.pid", "--logfile", "/tmp/mb.log", "--configfile", "/tmp/dyndns.json"]
