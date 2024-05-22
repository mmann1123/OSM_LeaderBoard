# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the current directory contents into the container at /usr/src/app
COPY . .

RUN pip install --upgrade pip

RUN apt-get update && apt-get install -y \
    binutils 

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Install PyInstaller
RUN pip install pyinstaller

# Build the executable using PyInstaller
# Replace 'main.py' with the entry point of your application
RUN pyinstaller --onefile --name leaderboard_linux dash_app.py

RUN cd dist &&  chmod -R +x ./leaderboard_linux

# The output executable will be in the 'dist' directory
