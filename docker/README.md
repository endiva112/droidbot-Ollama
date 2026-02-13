# 🐳 Docker Setup para DroidBot + Ollama

## 🚀 Inicio rápido
```bash
# Desde el directorio raíz del proyecto
cd docker
docker compose up -d
```

## 📦 Descargar modelo Ollama (primera vez)
```bash
docker exec -it droidbot-ollama ollama pull gemma3:4b
```

## ▶️ Ejecutar DroidBot
```bash
docker exec -it droidbot-app python start.py
```

O entrar al contenedor:
```bash
docker exec -it droidbot-app bash
# Ahora estás dentro con todo instalado
python start.py
```

## 🛠️ Desarrollo

### Editar código
- Edita archivos en tu máquina
- Los cambios se reflejan **instantáneamente** en el contenedor
- Solo reinicia el script Python

### Ver logs
```bash
docker compose logs -f
```

### Parar contenedores
```bash
docker compose down
```

### Reiniciar desde cero (borra todo, incluyendo modelo)
```bash
docker compose down -v
```

## 📝 Configuración

### Cambiar modelo de Ollama

Edita `docker-compose.yml`:
```yaml
environment:
  - OLLAMA_MODEL=gemma3:4b  # Cambia aquí
```

### Añadir dependencias Python

Edita `docker/requirements.txt`, luego:
```bash
docker compose build droidbot
docker compose up -d
```

## 🐛 Troubleshooting

**Ollama no responde:**
```bash
docker logs droidbot-ollama
```

**Error de conexión desde DroidBot:**
- Verifica que usas `http://ollama:11434` (NO `localhost`)
- Chequea que el healthcheck pase: `docker ps`

**Cambios de código no se ven:**
- Verifica el volumen: `docker exec -it droidbot-app ls -la /app`