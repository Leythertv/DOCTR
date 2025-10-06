# DOCTR - OCR Pipeline Multicapa con IA

[![Python](https://img.shields.io/badge/Python-3.7%2B-blue.svg)](https://python.org)
[![Ollama](https://img.shields.io/badge/Ollama-Supported-orange.svg)](https://ollama.ai)

## 🚀 Descripción General

DOCTR es un avanzado sistema de Reconocimiento Óptico de Caracteres (OCR) que utiliza un enfoque multicapa para lograr resultados superiores. Combina el poder de la librería **docTR** con modelos de visión (VLM) como **Qwen2.5-VL** para proporcionar extracción de texto precisa y mejorada.

## 🏗️ Arquitectura del Sistema

El pipeline funciona en tres capas principales:

### 1. **Capa de OCR Tradicional**
- Utiliza **docTR** para extracción inicial de texto
- Soporta múltiples formatos: PDF, JPG, PNG, y otros formatos de imagen
- Proporciona métricas de confianza para cada palabra detectada

### 2. **Capa de Mejora con IA (VLM)**
- Integra modelos de visión como **Qwen2.5-VL** a través de Ollama
- Compara visualmente la imagen original con el texto extraído por OCR
- Corrige errores de reconocimiento basándose en el análisis visual

### 3. **Capa de Post-procesamiento**
- Limpia y estructura los resultados según el tipo de tarea
- Ofrece múltiples formatos de salida: texto limpio, JSON estructurado, markdown

## ✨ Características Principales

- 🔄 **Procesamiento Multiformato**: Soporta múltiples formatos de imagen (JPG, PNG, etc.)
- 🧠 **Mejora con IA**: Utiliza VLMs para corregir errores del OCR tradicional
- 📊 **Múltiples Modos de Salida**: Texto limpio, JSON estructurado, resúmenes en markdown
- 🎯 **Alta Precisión**: Combinación de OCR tradicional + análisis visual
- 🔧 **Configurable**: Fácilmente adaptable a diferentes modelos VLM
- 📈 **Métricas de Confianza**: Evaluación de la calidad del reconocimiento
- 💾 **Guardado Automático**: Resultados guardados en JSON con numeración incremental

## 🛠️ Instalación

### Prerrequisitos

- Python 3.7 o superior
- [Ollama](https://ollama.ai/) instalado y corriendo
- Modelo Qwen2.5-VL descargado: `ollama pull qwen2.5vl:latest`

### Dependencias Python

```bash
pip install -r requirements.txt
```

O instalar manualmente:

```bash
pip install doctr requests python-doctr[torch]
```

### Configuración de Ollama

1. Instala [Ollama](https://ollama.ai/)
2. Inicia el servicio: `ollama serve`
3. Descarga el modelo: `ollama pull qwen2.5vl:latest`

## 🚀 Uso Rápido

### Uso Básico

```python
from ocr_pipeline import OCRPipeline

# Inicializar el pipeline
pipeline = OCRPipeline()

# Procesar un documento (solo imágenes actualmente)
results = pipeline.process_document("documento.jpg", tasks=["clean", "extract"])

# Guardar resultados
pipeline.save_results(results, "resultado.json")
```

### Modos de Procesamiento Disponibles

1. **"clean"**: Corrige errores del OCR basándose en análisis visual
2. **"extract"**: Extrae información clave en formato JSON
3. **"structure"**: Estructura el contenido en JSON organizado
4. **"summarize"**: Genera un resumen en formato markdown

### Ejemplo Completo

```python
# Inicializar con configuración personalizada
pipeline = OCRPipeline(
    ollama_url="http://localhost:11434",
    model_name="qwen2.5vl:latest"
)

# Procesar con múltiples tareas
tasks = ["clean", "extract", "summarize"]
results = pipeline.process_document("factura.jpg", tasks)  # Solo imágenes soportadas actualmente

# Los resultados incluyen:
# - results["ocr_raw"]: Resultado original del docTR
# - results["ai_clean"]: Texto corregido por la IA
# - results["ai_extract"]: Datos estructurados en JSON
# - results["ai_summarize"]: Resumen en markdown
```

## 📋 Estructura de Resultados

El sistema devuelve un diccionario con la siguiente estructura:

```json
{
  "ocr_raw": {
    "raw_text": "Texto extraído por docTR",
    "structured_data": {...},
    "confidence": 0.95
  },
  "ai_clean": "Texto corregido y mejorado",
  "ai_extract": [{"campo": "valor", "dato": "información"}],
  "ai_summarize": "# Documento\n\n## Contenido\n\nTexto estructurado en markdown"
}
```

## 🔧 Configuración Avanzada

### Cambiar Modelo VLM

```python
# Usar otro modelo compatible
pipeline = OCRPipeline(model_name="llava:latest")
```

### Configurar Ollama Remoto

```python
# Conectar a Ollama en otro servidor
pipeline = OCRPipeline(ollama_url="http://192.168.1.100:11434")
```

### Personalizar Prompts

Los prompts están definidos en el método `process_with_qwen()` y pueden ser modificados para adaptarse a necesidades específicas.

## 🎯 Casos de Uso

- **Digitalización de Imágenes**: Convertir imágenes de documentos a texto digital preciso
- **Procesamiento de Facturas**: Extraer datos estructurados de facturas y recibos (en formato imagen)
- **Análisis de Formularios**: Procesar formularios completados manualmente (en formato imagen)
- **Digitalización de Páginas**: Convertir páginas de libros a texto editable (en formato imagen)
- **Procesamiento de Documentos**: Extraer información clave de documentos (en formato imagen)

## 🔮 Roadmap Futuro

- [ ] **Soporte para PDF**: Procesamiento de documentos PDF
- [ ] Integración con APIs de modelos comerciales (OpenAI, Claude, etc.)
- [ ] Interfaz web para facilitar el uso
- [ ] Soporte para procesamiento por lotes
- [ ] Integración con bases de datos
- [ ] Modo de procesamiento asíncrono
- [ ] Soporte para más modelos VLM

## 🐛 Solución de Problemas

### Problemas Comunes

1. **Error de conexión con Ollama**
   - Asegúrate de que Ollama esté corriendo: `ollama serve`
   - Verifica que el modelo esté descargado: `ollama list`

2. **Problemas de codificación en Windows**
   - El script incluye configuración automática de UTF-8 para Windows
   - Si persisten problemas, ejecuta `chcp 65001` en la terminal

3. **Baja precisión en el OCR**
   - Asegúrate de que las imágenes tengan buena calidad
   - Considera preprocesar las imágenes (mejorar contraste, resolución)

## 📝 Requisitos del Sistema

- **Sistema Operativo**: Windows, Linux, macOS
- **Python**: 3.7 o superior
- **Memoria RAM**: Mínimo 4GB (recomendado 8GB+ para modelos grandes)
- **Almacenamiento**: 2GB para modelos de Ollama
- **GPU**: Opcional, pero recomendada para procesamiento más rápido

## 🤝 Contribuciones

¡Las contribuciones son bienvenidas! Por favor:

1. Fork este repositorio
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -m 'Agregando nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto es de código abierto. Si deseas utilizarlo, modificarlo o contribuir, siéntete libre de hacerlo. Para más información sobre licenciamiento, puedes contactar al maintainer.

## 🙏 Agradecimientos

- **[docTR](https://github.com/mindee/doctr)** - Excelente librería de OCR
- **[Qwen2.5-VL](https://huggingface.co/Qwen/Qwen2.5-VL)** - Modelo de visión utilizado
- **[Ollama](https://ollama.ai/)** - Plataforma para ejecutar modelos localmente

## 📞 Contacto

Para preguntas, sugerencias o reporte de issues:

- Crea un [issue](https://github.com/Leythertv/DOCTR/issues) en este repositorio
- Contacta al maintainer: Leythertv

---

**DOCTR** - Transformando documentos en conocimiento preciso y estructurado 🚀