# Use an official Python runtime as a parent image
FROM python:3.6-slim

# Set the working directory to /app
WORKDIR /ArrayTomographyTools

# Copy the current directory contents into the container at /app
ADD . /ArrayTomographyTools

# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt
