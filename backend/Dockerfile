# Use conda-forge/mambaforge:latest image
FROM condaforge/mambaforge:latest

# Set working directory
WORKDIR /app

# Copy environment file
COPY ../environment.yml .

# Create conda environment
RUN mamba env create -f environment.yml

# Make RUN commands use the new environment
SHELL ["conda", "run", "-n", "orthoviewer", "/bin/bash", "-c"]

# Copy application code
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 8000

# Run the application
CMD ["conda", "run", "--no-capture-output", "-n", "orthoviewer", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
