#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from doctr.io import DocumentFile
from doctr.models import ocr_predictor
import requests
import json
import os
import sys
from pathlib import Path

# Configuración agresiva de UTF-8 para Windows
if os.name == 'nt':  # Windows
    try:
        import subprocess
        subprocess.run(['chcp', '65001'], shell=True, capture_output=True)
        os.system('chcp 65001 > nul')
    except:
        pass
    
    # Forzar UTF-8 en Python
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    
    # Configurar locale
    try:
        import locale
        locale.setlocale(locale.LC_ALL, 'es_ES.UTF-8')
    except:
        try:
            locale.setlocale(locale.LC_ALL, '')
        except:
            pass


class OCRPipeline:
    def __init__(self, ollama_url="http://localhost:11434", model_name="qwen2.5vl:latest"):
        """
        Inicializar el pipeline OCR + IA
        """
        self.ollama_url = ollama_url
        self.model_name = model_name

        # Cargar modelo docTR
        print("Cargando modelo docTR...", flush=True)
        self.ocr_model = ocr_predictor(pretrained=True)
        print("Modelo docTR cargado", flush=True)

        # Verificar conexión con Ollama
        self._verify_ollama_connection()

    def _verify_ollama_connection(self):
        """Verificar que Ollama esté corriendo"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags")
            if response.status_code == 200:
                print("Conexión con Ollama verificada", flush=True)
            else:
                print("Error conectando con Ollama", flush=True)
        except Exception as e:
            print(f"Error: {e}", flush=True)

    def extract_text_doctr(self, file_path):
        """
        Extraer texto usando docTR de imágenes o PDFs
        """
        print(f"Procesando archivo: {file_path}", flush=True)
        
        # Determinar tipo de archivo
        file_extension = Path(file_path).suffix.lower()
        
        if file_extension == '.pdf':
            # Cargar PDF
            doc = DocumentFile.from_pdf(file_path)
            print(f"PDF cargado con {len(doc)} páginas", flush=True)
        else:
            # Cargar imagen (jpg, png, etc.)
            doc = DocumentFile.from_images(file_path)
            print("Imagen cargada", flush=True)

        # Procesar con OCR
        result = self.ocr_model(doc)

        # Extraer texto plano
        raw_text = result.render()

        # Extraer estructura detallada (opcional)
        structured_data = result.export()

        return {
            "raw_text": raw_text,
            "structured_data": structured_data,
            "confidence": self._calculate_confidence(structured_data),
        }

    def _calculate_confidence(self, structured_data):
        """Calcular confianza promedio del OCR"""
        confidences = []
        try:
            for page in structured_data["pages"]:
                for block in page["blocks"]:
                    for line in block["lines"]:
                        for word in line["words"]:
                            confidences.append(word["confidence"])
            return sum(confidences) / len(confidences) if confidences else 0
        except:
            return 0

    def process_with_qwen(self, text, image_path, task_type="clean"):
        """
        Procesar texto con Qwen, comparando con análisis visual de la imagen
        """
        import base64
        
        # Leer y codificar la imagen en base64
        with open(image_path, "rb") as img_file:
            image_base64 = base64.b64encode(img_file.read()).decode('utf-8')
        
        prompts = {
            "clean": f"""Analiza esta imagen y compárala con el siguiente texto extraído por OCR.
            
            TEXTO OCR (con errores):
            {text}
            
            Primero: Observa cuidadosamente la imagen y lee todo el texto que contiene.
            Segundo: Compara este texto visual con el texto OCR proporcionado arriba.
            Tercero: Corrige todos los errores del OCR basándote en lo que ves realmente en la imagen.
            Tercero: Corrige todos los errores del OCR basándote en lo que tu ves y lo que el texto del ocr extraido arriba te dio, asi podras completar o corregir y darme un mejor ocr. 
            Cuarto: Proporciona únicamente el texto corregido sin errores, con saltos de línea reales, no con \\n.
            
            IMPORTANTE: Devuelve el texto con formato real, no uses \\n para los saltos de línea, si vas a saltar de linea, inicial en el sigueinte no uses /n.""",
            
            "structure": f"""Analiza esta imagen y el siguiente texto extraído por OCR.
            
            TEXTO OCR (con errores):
            {text}
            
            Primero: Observa la imagen y lee todo el contenido visual.
            Segundo: Compara con el texto OCR y corrige los errores.
            Tercero: Estructura la información corregida en JSON identificando las secciones del documento.
            
            CRÍTICO: Responde SOLO con JSON válido, sin comillas triples, sin bloques de código, sin texto adicional.
            Ejemplo correcto: [{{"campo": "valor"}}]
            Ejemplo incorrecto: ```json [{{"campo": "valor"}}] ```""",
            
            "extract": f"""Analiza esta imagen y compárala con el siguiente texto extraído por OCR.
            
            TEXTO OCR (con errores):
            {text}
            
            Primero: Observa cuidadosamente la imagen para ver toda la información visual.
            Segundo: Compara con el texto OCR y corrige errores de reconocimiento.
            Tercero: Extrae la información clave corregida (nombres, fechas, números, direcciones, etc.).
            
            ABSOLUTAMENTE NECESARIO: Devuelve SOLO JSON válido, sin comillas triples, sin bloques de código, sin explicaciones.
            Formato correcto: [{{"nombre": "Juan"}}]
            Formato incorrecto: ```json [{{"nombre": "Juan"}}] ```""",
            
            "summarize": f"""Analiza esta imagen y el siguiente texto extraído por OCR.
            
            TEXTO OCR (con errores):
            {text}
            
            Primero: Observa la imagen y lee todo el contenido visual para entender el contexto.
            Segundo: Corrige el texto OCR basándote en lo que ves realmente.
            Tercero: Responde en formato markdown lo que se ve en el documento o imagen, manteniendo la estructura visual.
            
            IMPORTANTE:
            - Usa formato markdown con encabezados (#, ##, ###), listas, negritas (**texto**), etc.
            - Mantén la estructura visual del documento original
            - Usa saltos de línea reales, no \\n
            - No incluyas explicaciones ni resúmenes, solo muestra el contenido en markdown
            - Si hay tablas, reprodúcelas en formato markdown
            - Si hay formularios, muestra los campos y sus valores""",
        }

        prompt = prompts.get(task_type, prompts["clean"])

        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "images": [image_base64],
            "options": {"temperature": 0.1, "max_tokens": 2000},
        }

        try:
            response = requests.post(f"{self.ollama_url}/api/generate", json=payload)
            if response.status_code == 200:
                raw_response = response.json()["response"]
                # Limpiar la respuesta de la IA
                return self._clean_ai_response(raw_response, task_type)
            else:
                return f"Error en Ollama: {response.status_code}"
        except Exception as e:
            return f"Error conectando con Qwen: {e}"
    
    def _clean_ai_response(self, response, task_type):
        """Limpiar la respuesta de la IA eliminando caracteres de escape y formato no deseado"""
        if not response:
            return response
            
        # Eliminar bloques de código ```json ... ```
        response = response.replace("```json", "").replace("```", "")
        
        # Eliminar bloques de código ``` ... ```
        response = response.replace("```", "")
        
        # Para la tarea "summarize" (ahora formato markdown), preservar el formato
        if task_type == "summarize":
            # Eliminar solo "Resumen:" o títulos similares al inicio si existen
            response = response.replace("### Resumen:", "").replace("Resumen:", "").strip()
            # No eliminar viñetas ni numeración, ya que son parte del formato markdown
        
        # Para JSON, asegurar que esté bien formateado
        if task_type in ["structure", "extract"]:
            response = response.strip()
            # Si no empieza con [ o {, intentar extraer el JSON
            if not (response.startswith('[') or response.startswith('{')):
                # Buscar el primer [ o {
                start_idx = response.find('[')
                if start_idx == -1:
                    start_idx = response.find('{')
                if start_idx != -1:
                    response = response[start_idx:]
            
            # Si termina con texto después del JSON, eliminarlo
            if task_type == "extract" and response.startswith('['):
                # Encontrar el último ]
                last_bracket = response.rfind(']')
                if last_bracket != -1:
                    response = response[:last_bracket + 1]
        
        return response.strip()

    def process_document(self, file_path, tasks=["clean", "extract"]):
        """
        Pipeline completo: OCR + procesamiento IA para imágenes y PDFs
        """
        print(f"\nProcesando documento: {Path(file_path).name}", flush=True)
        print("=" * 50, flush=True)

        # Paso 1: Extraer texto con docTR
        ocr_result = self.extract_text_doctr(file_path)

        print(f"Texto extraído (confianza: {ocr_result['confidence']:.2f}):", flush=True)
        print("-" * 30, flush=True)
        texto_mostrado = ocr_result["raw_text"][:500] + "..." if len(ocr_result["raw_text"]) > 500 else ocr_result["raw_text"]
        print(texto_mostrado.encode('utf-8').decode('utf-8'), flush=True)

        # Paso 2: Procesar con Qwen según las tareas solicitadas
        results = {"ocr_raw": ocr_result}

        for task in tasks:
            print(f"\nProcesando con Qwen ({task})...", flush=True)
            ai_result = self.process_with_qwen(ocr_result["raw_text"], file_path, task)
            results[f"ai_{task}"] = ai_result

            print(f"Resultado ({task}):", flush=True)
            print("-" * 30, flush=True)
            resultado_mostrado = ai_result[:500] + "..." if len(str(ai_result)) > 500 else ai_result
            print(resultado_mostrado.encode('utf-8').decode('utf-8'), flush=True)

        return results

    def save_results(self, results, output_path="output.json"):
        """Guardar resultados en archivo JSON, evitando sobrescribir archivos existentes"""
        # Convertir a Path object para mejor manejo
        output_path = Path(output_path)
        
        # Si el archivo no existe, guardamos directamente
        if not output_path.exists():
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print(f"\nResultados guardados en: {output_path}", flush=True)
            return
        
        # Si el archivo ya existe, generar un nuevo nombre con sufijo numérico
        print(f"ADVERTENCIA: El archivo {output_path} ya existe", flush=True)
        
        # Extraer el nombre base y la extensión
        stem = output_path.stem
        suffix = output_path.suffix
        parent = output_path.parent
        
        # Buscar el siguiente número disponible
        counter = 1
        while True:
            # Formato: nombre_01.ext, nombre_02.ext, etc.
            new_stem = f"{stem}_{counter:02d}"
            new_path = parent / f"{new_stem}{suffix}"
            
            print(f"Verificando disponibilidad de: {new_path}", flush=True)
            
            if not new_path.exists():
                # Encontramos un nombre disponible
                with open(new_path, "w", encoding="utf-8") as f:
                    json.dump(results, f, ensure_ascii=False, indent=2)
                print(f"\nResultados guardados en: {new_path}", flush=True)
                return
            
            counter += 1
            # Límite de seguridad para evitar bucles infinitos
            if counter > 99:
                raise RuntimeError("No se pudo generar un nombre de archivo único después de 99 intentos")


# Función principal para usar el pipeline
def main():
    # Inicializar pipeline
    pipeline = OCRPipeline()

    # Procesar archivo (imagen o PDF - cambia la ruta por tu archivo)
    file_path = "11.jpg"  # ← Cambia esto por tu imagen o PDF

    if not os.path.exists(file_path):
        print(f"No se encontró el archivo: {file_path}", flush=True)
        print("Crea un archivo de prueba o cambia la ruta en el script", flush=True)
        return

    # Ejecutar pipeline con diferentes tareas
    tasks = ["clean", "extract", "summarize"]  # Puedes cambiar las tareas
    results = pipeline.process_document(file_path, tasks)

    # Guardar resultados
    pipeline.save_results(results, f"resultado_{Path(file_path).stem}.json")


if __name__ == "__main__":
    main()
