# Token-Efficient Agent Docker Image
# Minimal Python environment for data analysis

FROM python:3.12-slim

# Install Python data analysis packages
RUN pip install --no-cache-dir \
    pandas \
    numpy \
    matplotlib \
    scikit-learn

# Set working directory
WORKDIR /workspace

# Keep container running
CMD ["tail", "-f", "/dev/null"]
