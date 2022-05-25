# pull official base image
FROM python:3.9.5-slim-buster

RUN apt-get update
RUN apt-get install ffmpeg libsm6 libxext6  -y

COPY . .
RUN mkdir static
RUN pip install -r requirements.txt
EXPOSE 80
CMD ["flask", "run", "--host=0.0.0.0", "--port=80"]