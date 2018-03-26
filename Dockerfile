FROM fire:base

COPY src /usr/src

ENV PYTHONPATH /usr/src

EXPOSE 5000

CMD ["python", "-m", "controller_app", "--"]