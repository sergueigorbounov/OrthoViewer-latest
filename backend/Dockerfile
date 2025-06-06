# Use conda-forge/mambaforge:latest image
FROM condaforge/mambaforge:latest

# Set working directory
WORKDIR /app

# Copy environment file
COPY ./environment.yml .

# Create conda environment
RUN mamba env create -f environment.yml

# Copy application code
COPY . .

# Set environment variables for headless operation
ENV PYTHONUNBUFFERED=1
ENV QT_QPA_PLATFORM=offscreen
ENV DISPLAY=

# Expose port
EXPOSE 8002

# Run the application with proper conda activation
CMD ["conda", "run", "--no-capture-output", "-n", "orthoviewer2", "python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8002"]
