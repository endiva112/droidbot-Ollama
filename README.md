DroidBot + Ollama
Herramienta para testing automático de apps Android guiado por IA local (Ollama).

📋 Requisitos previos

Ubuntu 24.04 (o similar)
Android Studio con un emulador configurado
ADB instalado: sudo apt install adb
Ollama instalado: https://ollama.com/download


🚀 Instalación
## 1. Clonar repositorio
```bash
git clone https://github.com/endiva112/droidbot-Ollama.git
```

```bash
cd droidbot-Ollama
```

## 2. Instalar Python 3.10
```bash
sudo apt install software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.10 python3.10-venv python3.10-dev
```

## 3. Crear entorno virtual e instalar dependencias
```bash
python3.10 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install setuptools androguard==3.4.0a1 networkx Pillow requests
```

## 4. Descargar modelo de Ollama
bashollama pull gemma2:2b

▶️ Uso
1. Arrancar emulador Android
Abre Android Studio → AVD Manager → Run (ej: Pixel 6)
2. Configurar ADB
bashadb devices
# Anota el nombre del dispositivo (ej: emulator-5554)
3. Extraer APK de la app a testear
bash# Listar apps instaladas
adb shell pm list packages | grep <nombre_app>

# Obtener ruta del APK
adb shell pm path <package_name>

# Descargar APK
adb pull <ruta_del_apk> app.apk
Ejemplo con la app Reloj:
```bash
adb shell pm path com.google.android.deskclock
adb pull /product/app/PrebuiltDeskClockGoogle/PrebuiltDeskClockGoogle.apk reloj.apk
```
4. Ejecutar DroidBot
```bash
python start.py -d <dispositivo> -a <apk> -policy llm_guided -count 30 -o resultados
```
Ejemplo:
```bash
python start.py -d emulator-5554 -a reloj.apk -policy llm_guided -count 30 -o resultados_reloj
```

📊 Resultados
Los resultados se guardan en la carpeta especificada con -o:

- ```utg.js``` - Grafo de la interfaz explorada
- ```events/``` - Eventos ejecutados
- ```states/``` - Capturas de pantalla de cada estado


⚠️ Problemas comunes
"Accessibility errors" en bucle:

Cancela (Ctrl+C) y vuelve a ejecutar el comando. Suele funcionar a la segunda.

"more than one device/emulator":

Usa -d <nombre_dispositivo> para especificar cuál usar: adb devices para ver la lista.

"ModuleNotFoundError: No module named 'androguard.core.bytecodes'":

Desinstala e instala la versión correcta: pip uninstall androguard && pip install androguard==3.4.0a1


📝 Notas

Cada ejecución con LLM puede tardar 10-15 minutos dependiendo del hardware.
El modelo gemma2:2b es más rápido que gemma3:4b.
Ajusta -count para controlar cuántas interacciones hacer (más = más tiempo).