FROM python:3.12-slim
WORKDIR /app
ENV PYTHONUNBUFFERED=1
COPY monitorias ./monitorias
VOLUME ["/datos"]
ENTRYPOINT ["python", "-m", "monitorias"]
CMD ["/datos/monitorias.json"]
