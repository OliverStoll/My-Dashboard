FROM python:3.12
ENV DOCKER_WORKDIR="/app"
WORKDIR $DOCKER_WORKDIR
COPY pyproject.toml ./
RUN pip install poetry
RUN poetry config virtualenvs.create false
RUN poetry install --with cloud --without dev
# make sure the following line is still "COPY . /app"
# (sometimes gets changed when moving files)
COPY . /app

EXPOSE 8080
CMD ["python", "./src/cloud_entry.py"]
