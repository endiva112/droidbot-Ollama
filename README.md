# 🤖 DroidBot + Ollama: Exploración Guiada por IA

Integración de Ollama (LLM local) con DroidBot para exploración inteligente de apps Android.

## 🎯 ¿Qué hace?

En lugar de tocar botones aleatoriamente, **Ollama decide** qué acciones tomar basándose en el estado actual de la interfaz de la app.

## 🚀 Instalación Rápida

### 1. Verifica que Ollama funciona

```bash
python test_ollama.py
```

Debe pasar los 3 tests. Si falla:
```bash
# Inicia Ollama
ollama serve

# Descarga un modelo (en otra terminal)
ollama pull gemma2:2b
```

### 2. Instala el archivo en DroidBot

```bash
# Copia input_policy3.py a tu fork de DroidBot
cp input_policy3.py /ruta/a/tu/droidbot-fork/droidbot/

# Verifica que se importa correctamente
cd /ruta/a/tu/droidbot-fork
python -c "from droidbot.input_policy3 import LLM_Guided_Policy; print('✓ OK')"
```

### 3. ¡Usa DroidBot con Ollama!

```bash
python -m droidbot \
    -a tu_app.apk \
    -o resultados/ \
    -policy llm_guided \
    -count 100
```

## ⚙️ Configuración

### Cambiar modelo de Ollama

Usa variables de entorno:

```bash
export OLLAMA_MODEL="llama3"
python -m droidbot -policy llm_guided ...
```

O modifica `input_policy3.py` línea 25:
```python
self.ollama_model = ollama_model or os.getenv("OLLAMA_MODEL", "llama3")
```

### Ollama en otro servidor

```bash
export OLLAMA_URL="http://192.168.1.100:11434/api/chat"
python -m droidbot -policy llm_guided ...
```

## 📊 Modelos recomendados

| Modelo | Tamaño | Velocidad | Calidad |
|--------|--------|-----------|---------|
| `gemma2:2b` | 1.6 GB | ⚡⚡⚡ Muy rápido | ⭐⭐ Básica |
| `gemma2:9b` | 5.5 GB | ⚡⚡ Rápido | ⭐⭐⭐ Buena |
| `llama3` | 4.7 GB | ⚡⚡ Rápido | ⭐⭐⭐ Buena |
| `llama3:70b` | 40 GB | ⚡ Lento | ⭐⭐⭐⭐⭐ Excelente |

Para descargar:
```bash
ollama pull gemma2:9b
```

## 🔍 ¿Cómo funciona?

```
┌─────────────────────────────────────────┐
│  1. DroidBot captura estado de la app  │
│     (actividad, botones, inputs...)     │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  2. Construye prompt para Ollama:       │
│                                          │
│     "Opciones disponibles:              │
│      0. Touch 'Login'                   │
│      1. Touch 'Register'                │
│      2. Scroll DOWN                     │
│      3. Press BACK                      │
│                                          │
│     ¿Qué acción elegir?"                │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  3. Ollama responde: "1"                │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  4. DroidBot ejecuta: Touch 'Register'  │
└─────────────────────────────────────────┘
```

## 📁 Archivos incluidos

- **`input_policy3.py`** ⭐ - El archivo principal (cópialo a droidbot/)
- **`test_ollama.py`** - Script de prueba
- **`INTEGRACION_OLLAMA.md`** - Guía detallada
- **`input_policy_ollama.py`** - Versión alternativa (no necesaria)
- **`input_manager_example.py`** - Ejemplo de referencia

## 🐛 Solución de problemas

### "Could not connect to Ollama"

```bash
# Verifica que Ollama está corriendo
curl http://localhost:11434/api/tags

# Si no responde, inicia Ollama
ollama serve
```

### "Module 'input_policy3' not found"

```bash
# Verifica la ruta del archivo
ls /ruta/a/droidbot/droidbot/input_policy3.py

# Debe existir en el mismo directorio que input_policy.py
```

### Ollama siempre elige acciones aleatorias

1. Prueba con un modelo más grande: `llama3` o `gemma2:9b`
2. Revisa los logs para ver qué responde Ollama:
   ```bash
   python -m droidbot ... --debug 2>&1 | grep -i ollama
   ```

## 📈 Mejoras futuras

Ideas para extender la funcionalidad:

1. **Análisis visual**: Enviar screenshots a modelos con visión (LLaVA)
2. **Memoria de exploración**: Evitar loops recordando acciones previas
3. **Objetivos dirigidos**: "Encuentra el botón de login"
4. **Respuestas estructuradas**: Usar JSON para respuestas más ricas
5. **Documentación automática**: Ollama describe lo que hace cada pantalla

## 📚 Más información

- [DroidBot oficial](https://github.com/honeynet/droidbot)
- [Ollama oficial](https://ollama.ai/)
- [Documentación de modelos](https://ollama.ai/library)

## 🙋 Contribuir

Si mejoras esta integración, considera:
- Compartir tus prompts optimizados
- Reportar bugs con modelos específicos
- Sugerir nuevas estrategias de exploración

---

**¿Preguntas?** Revisa `INTEGRACION_OLLAMA.md` para la guía detallada.