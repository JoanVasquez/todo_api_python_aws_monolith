FROM python:3.9-alpine3.13
LABEL maintainer="joanvasquez"

# Recommended to keep Python output unbuffered
ENV PYTHONUNBUFFERED=1

# Copy requirements and app code
COPY ./requirements.txt /tmp/requirements.txt
COPY ./requirements.dev.txt /tmp/requirements.dev.txt
COPY ./app /app

WORKDIR /app
EXPOSE 8000

# Build argument to control dev installation
ARG DEV=false

# Create a virtual environment, install system dependencies,
# then install Python packages.
RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    apk add --update --no-cache postgresql-client && \
    apk add --update --no-cache --virtual .tmp-build-deps \
    build-base postgresql-dev musl-dev && \
    /py/bin/pip install -r /tmp/requirements.txt && \
    if [ "$DEV" = "true" ]; then \
    /py/bin/pip install -r /tmp/requirements.dev.txt; \
    fi && \
    rm -rf /tmp && \
    apk del .tmp-build-deps && \
    adduser -D -H django-user

ENV PATH="/py/bin:$PATH"

USER django-user

# Use CMD to run Django’s commands on container start.
CMD ["sh", "-c", "python manage.py wait_for_db && \
    python manage.py migrate && \
    python manage.py runserver 0.0.0.0:8000"]
