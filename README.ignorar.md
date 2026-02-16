TODO# 🤖 DroidBot + Ollama

Exploración automática de apps Android guiada por IA local (Ollama).

---

## 🚀 Instalación

### 0. Clonar el repositorio

```bash
git clone https://github.com/tu-usuario/droidbot-Ollama.git
cd droidbot-Ollama
```

---

### 1. Configurar entorno Docker

```bash
cd docker
# Leer docker/README.md para instrucciones de Docker
```

---

### 2. Estructura del proyecto

```
droidbot-Ollama/
├── docker/              # Configuración Docker (Dockerfile, docker-compose.yml)
├── droidbot/            # Fork de DroidBot con input_policy3.py
├── script_samples/      # Scripts de ejemplo
├── start.py             # Script de inicio alternativo
└── README.md            # Este archivo
```

---

### 3. Configurar ADB

**ADB** (Android Debug Bridge) es necesario para conectar con dispositivos/emuladores Android.

#### Windows

Si usas **Android Studio**, ADB ya está instalado en:
```
C:\Users\TU_USUARIO\AppData\Local\Android\Sdk\platform-tools
```

**Añadir al PATH:**
1. Windows + R → `sysdm.cpl` → Enter
2. Variables de entorno → Path → Editar → Nuevo
3. Pegar: `C:\Users\TU_USUARIO\AppData\Local\Android\Sdk\platform-tools`
4. Aceptar todo y reiniciar terminal

**Verificar:**
```powershell
adb version
```

#### Linux

```bash
sudo apt-get install android-tools-adb android-tools-fastboot
```

#### Mac

```bash
brew install android-platform-tools
```

---

### 4. Preparar emulador/dispositivo

#### Opción A: Emulador de Android Studio

1. Inicia el emulador desde Android Studio
2. Activa modo TCP (solo una vez):
   ```bash
   adb tcpip 5555
   ```

#### Opción B: Dispositivo físico

1. Activa "Depuración USB" en el dispositivo
2. Conecta por USB
3. Autoriza la conexión en el dispositivo

---

## 🎮 Uso

### Ejemplo: Explorar app de Reloj

```bash
# 1. Iniciar Docker
cd docker
docker-compose up -d

# 2. Descargar modelo Ollama
docker-compose exec ollama ollama pull gemma3:4b

# 3. Entrar al contenedor
docker-compose exec droidbot bash
```

**Dentro del contenedor:**

```bash
# 4. Conectar ADB al emulador del host
adb connect host.docker.internal:5555

# 5. Verificar dispositivos
adb devices
# Debe mostrar: host.docker.internal:5555   device

# 6. Buscar paquete de la app de reloj
adb shell pm list packages | grep clock
# Salida típica: com.google.android.deskclock

# 7. Ejecutar DroidBot con Ollama
python -m droidbot \
    -p com.google.android.deskclock \
    -policy llm_guided \
    -count 30 \
    -o /app/resultados \
    -grant_perm
```

**Resultados:** Los encontrarás en `droidbot-Ollama/resultados/`

---

## 🔧 Configuración

### Cambiar modelo de Ollama

Edita `docker/docker-compose.yml`:

```yaml
environment:
  - OLLAMA_MODEL=llama3  # Cambiar aquí
```

Modelos disponibles: https://ollama.ai/library

---

## 🐛 Solución de problemas

### "adb: device not found"

```bash
# Dentro del contenedor
adb connect host.docker.internal:5555
adb devices
```

### "Could not connect to Ollama"

```bash
# Verificar que Ollama está corriendo
docker-compose exec ollama ollama list

# Si está vacío, descargar modelo
docker-compose exec ollama ollama pull gemma3:4b
```

### "Module 'input_policy3' not found"

```bash
# Verificar que existe
ls droidbot/input_policy3.py
```

---

## 📚 Documentación adicional

- **Docker:** `docker/README.md`
- **DroidBot oficial:** https://github.com/honeynet/droidbot
- **Ollama:** https://ollama.ai/