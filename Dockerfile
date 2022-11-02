# Copyright (c) 2022 Cohere Inc. and its affiliates.
#
# Licensed under the MIT License (the "License");
# you may not use this file except in compliance with the License.
#
# You may obtain a copy of the License in the LICENSE file at the top
# level of this repository.

FROM python:3.10.4


# Cloud Run compatibility for built artifacts
ENV PYTHONDONTWRITEBYTECODE=1
ENV POETRY_VIRTUALENVS_CREATE=false

# rebuild on dependency changes
COPY ./poetry.lock ./pyproject.toml ./
RUN pip3 install poetry
RUN poetry install --no-root --no-dev

# pre-create data directory
RUN mkdir /data

# rebuild on file changes
WORKDIR /app
COPY . .

CMD [ "uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "8080" ]
