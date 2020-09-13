FROM python:3.6
RUN apt-get update
RUN pip install Flask flask-cors Pillow randomcolor

RUN useradd -ms /bin/bash admin
RUN mkdir -p /app/static
RUN chown admin /app/static
USER admin
WORKDIR /app
COPY app /app
CMD ["flask", "run"]
