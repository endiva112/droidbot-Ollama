FROM python:3.10-slim

WORKDIR /app

# Dependencias del sistema
RUN apt-get update && apt-get install -y \
    # Utilidades básicas
    curl \
    git \
    # ADB y herramientas Android (ESTO FALTABA)
    android-tools-adb \
    android-tools-fastboot \
    # Dependencias de OpenCV (probablemente las necesites)
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    # Limpieza
    && rm -rf /var/lib/apt/lists/*

# Instalar paquetes Python
COPY docker/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Verificar que ADB se instaló correctamente
RUN adb version

CMD ["bash"]