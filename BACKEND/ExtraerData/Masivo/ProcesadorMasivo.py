import os, zipfile
from pathlib import Path
from typing import List, Dict
from tkinter import messagebox
from ..Normal.Extractor import DocumentExtractor
from ..Normal.Archivos import FileProcessor
from ..Normal.Excel import ExcelExporter
from ..Normal.Configuracion import logger

class MassiveProcessor:
    
    def __init__(self):
        # Inicializa los componentes principales: extractor de documentos, procesador de archivos y exportador a Excel
        self.extractor = DocumentExtractor()
        self.file_processor = FileProcessor()
        self.excel_exporter = ExcelExporter()
        self.processing = False
        self.current_progress = 0
        self.total_items = 0
        
    def process_massive(self, main_folder_path: str, progress_callback=None, status_callback=None) -> str:
        # Función principal que coordina el procesamiento masivo de carpetas y archivos ZIP
        try:
            self.processing = True
            self.current_progress = 0
            
            if status_callback:
                status_callback("Buscando subcarpetas y archivos comprimidos...")
            
            # Encuentra todos los elementos a procesar (subcarpetas y archivos ZIP)
            items_to_process = self.find_processing_items(main_folder_path)
            self.total_items = len(items_to_process)
            
            if self.total_items == 0:
                if status_callback:
                    status_callback("No se encontraron subcarpetas ni archivos ZIP para procesar.")
                return ""
            
            # Crea directorio temporal para almacenar resultados intermedios
            temp_results_dir = Path.home() / "Downloads" / "resultados_temporales"
            temp_results_dir.mkdir(exist_ok=True)
            
            excel_files = []
            
            # Procesa cada elemento encontrado (carpeta o ZIP)
            for idx, (item_path, item_name, is_zip) in enumerate(items_to_process, 1):
                if status_callback:
                    status_callback(f"Procesando: {item_name}")
                
                try:
                    # Procesa un elemento individual y guarda el archivo resultante
                    result_file = self.process_single_item(item_path, item_name, is_zip, temp_results_dir)
                    if result_file:
                        excel_files.append(result_file)
                    
                    # Actualiza la barra de progreso
                    self.current_progress = (idx / self.total_items) * 100
                    if progress_callback:
                        progress_callback(self.current_progress)
                        
                except Exception as e:
                    logger.error(f"Error procesando {item_name}: {e}")
                    if status_callback:
                        status_callback(f"Error en {item_name}: {str(e)}")
            
            # Crea archivo ZIP final con todos los Excel generados
            if excel_files:
                zip_path = self.create_results_zip(excel_files, main_folder_path)
                
                # Limpia los archivos temporales creados durante el procesamiento
                self.cleanup_temp_files(temp_results_dir)
                
                if status_callback:
                    status_callback("Procesamiento masivo completado exitosamente.")
                
                return zip_path
            else:
                if status_callback:
                    status_callback("No se generaron archivos Excel.")
                return ""
                
        except Exception as e:
            logger.error(f"Error en procesamiento masivo: {e}")
            if status_callback:
                status_callback(f"Error: {str(e)}")
            return ""
        finally:
            self.processing = False
    
    def find_processing_items(self, main_folder_path: str) -> List[tuple]:
        # Busca y retorna todas las subcarpetas y archivos ZIP dentro del directorio principal
        items = []
        
        # Recorre el directorio principal buscando subcarpetas
        for item in os.listdir(main_folder_path):
            item_path = os.path.join(main_folder_path, item)
            if os.path.isdir(item_path):
                items.append((item_path, item, False))
        
        # Busca archivos ZIP en el directorio principal
        for item in os.listdir(main_folder_path):
            item_path = os.path.join(main_folder_path, item)
            if os.path.isfile(item_path) and item.lower().endswith('.zip'):
                items.append((item_path, item, True))
        
        return items
    
    def process_single_item(self, item_path: str, item_name: str, is_zip: bool, output_dir: Path) -> str:
        # Procesa un elemento individual (carpeta o archivo ZIP) extrayendo datos de PDFs y generando Excel
        work_folder = item_path
        
        # Si es un ZIP, lo extrae primero a una carpeta temporal
        if is_zip:
            work_folder = self.file_processor.extract_compressed_file(item_path)
        
        try:
            # Busca todos los archivos PDF dentro del elemento
            pdf_files = self.file_processor.find_pdf_files(work_folder)
            
            if not pdf_files:
                logger.warning(f"No se encontraron PDFs en: {item_name}")
                return ""
            
            # Extrae datos de cada PDF encontrado
            extracted_data = []
            for pdf_path in pdf_files:
                pdf_filename = os.path.basename(pdf_path)
                try:
                    text = self.extractor.extract_text_from_pdf(pdf_path)
                    document_data = self.extractor.extract_document_data(text, pdf_filename)
                    if document_data:
                        extracted_data.append(document_data)
                except Exception as e:
                    logger.error(f"Error procesando {pdf_filename}: {e}")
            
            if not extracted_data:
                logger.warning(f"No se extrajeron datos válidos de: {item_name}")
                return ""
            
            # Limpia el nombre del elemento para usarlo como nombre de archivo
            if is_zip and item_name.lower().endswith('.zip'):
                clean_item_name = self.clean_filename(item_name[:-4])  # Remueve extensión .zip
            else:
                clean_item_name = self.clean_filename(item_name)
            
            # Exporta los datos extraídos a un archivo Excel
            excel_path = self.excel_exporter.export_to_excel_massive(
                extracted_data, clean_item_name, output_dir
            )
            
            return excel_path
            
        finally:
            # Limpia archivos temporales si el elemento era un ZIP
            if is_zip:
                self.file_processor.cleanup_temp_files()
    
    def create_results_zip(self, excel_files: List[str], main_folder_path: str) -> str:
        # Crea un archivo ZIP que contiene todos los archivos Excel generados
        zip_path = os.path.join(main_folder_path, "excel_con_resultados.zip")
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for excel_file in excel_files:
                zipf.write(excel_file, os.path.basename(excel_file))
        
        logger.info(f"ZIP creado exitosamente: {zip_path}")
        return zip_path
    
    def cleanup_temp_files(self, temp_dir: Path):
        # Elimina todos los archivos temporales y el directorio temporal
        try:
            for file in temp_dir.glob("*"):
                file.unlink()
            temp_dir.rmdir()
        except Exception as e:
            logger.error(f"Error limpiando archivos temporales: {e}")
    
    def clean_filename(self, filename: str) -> str:
        # Limpia el nombre de archivo removiendo caracteres inválidos y limitando su longitud
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        return filename[:50]  # Limita la longitud del nombre