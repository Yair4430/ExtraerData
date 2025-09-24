from flask import Flask, request, jsonify
from flask_cors import CORS
from ExtraerData.Normal.archivos import FileProcessor
from ExtraerData.Normal.extractor import DocumentExtractor
from ExtraerData.Normal.excel import ExcelExporter
from ExtraerData.Masivo.procesadorMasivo import MassiveProcessor  
from ExtraerData.Normal.configuracion import logger
import os,threading

# Configuración inicial de la aplicación Flask con soporte CORS
app = Flask(__name__)
CORS(app)  # Habilita CORS para permitir peticiones desde diferentes dominios

# Diccionario global para almacenar el estado de progreso de cada procesamiento masivo
massive_processing_status = {}

@app.route("/procesar", methods=["POST"])
def procesar_archivos():
    # Endpoint para procesamiento individual de archivos o carpetas con documentos PDF
    try:
        data = request.get_json()
        ruta = data.get("ruta")
        ficha = data.get("ficha", "default")

        if not ruta or not os.path.exists(ruta):
            return jsonify({"error": "La ruta proporcionada no existe"}), 400

        # Inicializa los componentes necesarios para el procesamiento
        file_processor = FileProcessor()
        extractor = DocumentExtractor()
        excel_exporter = ExcelExporter()

        # Maneja diferentes tipos de entrada: archivos comprimidos o carpetas
        if os.path.isfile(ruta) and ruta.lower().endswith((".zip", ".rar")):
            carpeta_trabajo = file_processor.extract_compressed_file(ruta)
        elif os.path.isdir(ruta):
            carpeta_trabajo = ruta
        else:
            return jsonify({"error": "Debe ser una carpeta, un .zip o un .rar válido"}), 400

        # Busca todos los archivos PDF en la carpeta de trabajo
        pdf_files = file_processor.find_pdf_files(carpeta_trabajo)

        if not pdf_files:
            return jsonify({"error": "No se encontraron archivos PDF"}), 400

        # Procesa cada PDF encontrado extrayendo su texto y datos estructurados
        documentos_extraidos = []
        for pdf in pdf_files:
            try:
                text = extractor.extract_text_from_pdf(pdf)
                doc_data = extractor.extract_document_data(text, os.path.basename(pdf))
                if doc_data:
                    documentos_extraidos.append(doc_data)
            except Exception as e:
                logger.error(f"Error procesando {pdf}: {e}")

        if not documentos_extraidos:
            return jsonify({"error": "No se pudo extraer información de los PDFs"}), 400

        # Exporta los datos extraídos a un archivo Excel
        excel_path = excel_exporter.export_to_excel(documentos_extraidos, ficha)

        # Limpia archivos temporales si se extrajeron de archivos comprimidos
        file_processor.cleanup_temp_files()

        return jsonify({"message": "Proceso completado con éxito", "excel_path": excel_path, "documentos_procesados": len(documentos_extraidos)})

    except Exception as e:
        logger.error(f"Error en /procesar: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/procesar-masivo", methods=["POST"])
def procesar_masivo():
    # Endpoint para iniciar procesamiento masivo de múltiples carpetas/archivos ZIP
    try:
        data = request.get_json()
        ruta = data.get("ruta")
        process_id = data.get("process_id", "default_massive_process")

        if not ruta or not os.path.exists(ruta):
            return jsonify({"error": "La ruta proporcionada no existe"}), 400

        if not os.path.isdir(ruta):
            return jsonify({"error": "La ruta debe ser una carpeta para procesamiento masivo"}), 400

        # Inicializa el estado del procesamiento en el diccionario global
        massive_processing_status[process_id] = {"status": "processing", "progress": 0, "message": "Iniciando procesamiento...", "result": None, "error": None}

        # Ejecuta el procesamiento en un hilo separado para no bloquear la aplicación
        thread = threading.Thread(
            target=run_massive_processing,
            args=(ruta, process_id)
        )
        thread.daemon = True
        thread.start()

        return jsonify({ "message": "Procesamiento masivo iniciado", "process_id": process_id, "status_url": f"/procesar-masivo/status/{process_id}"})

    except Exception as e:
        logger.error(f"Error iniciando procesamiento masivo: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/procesar-masivo/status/<process_id>", methods=["GET"])
def get_massive_status(process_id):
    # Endpoint para consultar el estado actual de un procesamiento masivo en curso
    if process_id not in massive_processing_status:
        return jsonify({"error": "ID de proceso no encontrado"}), 404

    status_data = massive_processing_status[process_id]
    return jsonify(status_data)

@app.route("/procesar-masivo/result/<process_id>", methods=["GET"])
def get_massive_result(process_id):
    # Endpoint para obtener el resultado final de un procesamiento masivo completado
    if process_id not in massive_processing_status:
        return jsonify({"error": "ID de proceso no encontrado"}), 404

    status_data = massive_processing_status[process_id]
    
    if status_data["status"] == "completed" and status_data["result"]:
        return jsonify({"status": "completed","result": status_data["result"]})
    elif status_data["status"] == "error":
        return jsonify({"status": "error", "error": status_data["error"]})
    else:
        return jsonify({"status": "processing", "message": "El procesamiento aún está en curso"})

def run_massive_processing(ruta, process_id):
    # Función que ejecuta el procesamiento masivo en un hilo separado
    try:
        processor = MassiveProcessor()
        
        # Callbacks para actualizar el progreso y estado durante el procesamiento
        def progress_callback(progress):
            massive_processing_status[process_id]["progress"] = progress
        
        def status_callback(message):
            massive_processing_status[process_id]["message"] = message
            massive_processing_status[process_id]["progress"] = massive_processing_status[process_id].get("progress", 0)
        
        # Ejecuta el procesamiento masivo principal
        zip_path = processor.process_massive(ruta, progress_callback, status_callback)
        
        # Actualiza el estado final según el resultado del procesamiento
        if zip_path:
            massive_processing_status[process_id] = {"status": "completed", "progress": 100, "message": "Procesamiento masivo completado exitosamente",
                "result": {
                    "zip_path": zip_path,
                    "message": "Todos los archivos han sido procesados y comprimidos"
                },
                "error": None
            }
        else:
            massive_processing_status[process_id] = {"status": "error","progress": 0,"message": "No se generaron resultados","result": None, "error": "No se encontraron archivos para procesar o ocurrió un error"}
            
    except Exception as e:
        logger.error(f"Error en procesamiento masivo: {e}")
        massive_processing_status[process_id] = {"status": "error","progress": 0,"message": "Error durante el procesamiento","result": None,"error": str(e)}

if __name__ == "__main__":
    # Inicia el servidor Flask en modo debug
    app.run(debug=True)