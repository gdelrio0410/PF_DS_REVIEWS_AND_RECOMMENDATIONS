FROM python:3.9-slim


RUN apt-get update && \
    apt-get install -y build-essential libmariadb-dev pkg-config && \
    apt-get clean

COPY . /app


WORKDIR /app


RUN pip install -r requirements.txt

EXPOSE 80

ENV STREAMLIT_SERVER_PORT=8501


CMD ["streamlit", "run", "main.py"]


