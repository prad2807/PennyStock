#!/bin/bash

echo "Installing backend dependencies..."
cd backend
python3 -m pip install --upgrade pip setuptools wheel
python3 -m pip install fastapi
python3 -m pip install uvicorn
python3 -m pip install pydantic
python3 -m pip install SQLAlchemy
python3 -m pip install celery
python3 -m pip install redis
python3 -m pip install pytest

echo "Backend dependencies installed!"
cd ..

echo "Installing frontend dependencies..."
cd frontend
npm install
echo "Frontend dependencies installed!"

echo "Setup complete!"
