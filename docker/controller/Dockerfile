FROM fire/base:1.0

COPY src /usr/src

ENV PYTHONPATH /usr/src

EXPOSE 5000

ENTRYPOINT ["python", "-m", "controller_app"]