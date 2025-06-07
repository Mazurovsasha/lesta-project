#!/bin/sh

echo "Starting entrypoint script..."


if [ ! -d "./migrations" ]; then
  echo "Migrations folder not found, initializing migrations..."
  flask db init
  flask db migrate -m "Initial migration"
fi

  
echo "Applying migrations..."
flask db upgrade

echo "Starting Gunicorn..."
exec gunicorn --bind 0.0.0.0:5000 "app:create_app()"
