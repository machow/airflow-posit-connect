FROM jupyter/r-notebook:notebook-6.5.2
#FROM python:3.9.1-slim-buster
USER root

# Postgres Requirements (For our Metadata Database)
RUN apt-get update && apt-get install -y libpq-dev build-essential


RUN pip3 install psycopg2

# Install airflow and gusty
RUN pip3 install \
    apache-airflow==2.3.4 \
    gusty==0.16.0 \
    siuba==0.4.2 \
    duckdb_engine==0.6.8 \
    pyarrow==11.0.0 \
    jupytext==1.14.4 \
    fsspec==2023.1.0 \
    git+https://github.com/rstudio/pins-python.git@d6b31437bf7edb7a99e5e9459a99d073e4e0ae89 \
    rsconnect-python

RUN pip3 install git+https://github.com/machow/dbcooper-py.git@9a5eea3efa3693bcf82804a3313289c9b8550404
RUN pip3 install git+https://github.com/machow/gh_api.git@8e4ff69887bff58032014b0745eab4af8622a28a

Run Rscript -e 'install.packages("rsconnect", repos="http://cran.rstudio.com/")'

USER ${NB_UID}

# Airflow Env Vars
ENV AIRFLOW_HOME='/usr/local/airflow'

# Set wd
#WORKDIR /usr/local/airflow

# Sleep forever
# CMD sleep infinity
