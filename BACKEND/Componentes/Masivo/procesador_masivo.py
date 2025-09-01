import os
import zipfile
import threading
from pathlib import Path
from typing import List, Dict
from tkinter import messagebox
from ..Normal.extractor import DocumentExtractor
from ..Normal.archivos import FileProcessor
from ..Normal.excel import ExcelExporter
from ..Normal.configuracion import logger

class MassiveProcessor:
    """Clase para procesamiento masivo de múltiples carpetas/archivos"""
    
    def __init__(self):
        self.extractor = DocumentExtractor()
        self.file_processor = FileProcessor()
        self.excel_exporter = ExcelExporter()
        self.processing = False
        self.current_progress = 0
        self.total_items = 0
        
    def process_massive(self, main_folder_path: str, progress_callback=None, status_callback=None) -> str:
        """Procesa todas las subcarpetas y archivos ZIP en la carpeta principal"""
        try:
            self.processing = True
            self.current_progress = 0
            
            if status_callback:
                status_callback("Buscando subcarpetas y archivos comprimidos...")
            
            # Encontrar todas las subcarpetas y archivos ZIP
            items_to_process = self.find_processing_items(main_folder_path)
            self.total_items = len(items_to_process)
            
            if self.total_items == 0:
                if status_callback:
                    status_callback("No se encontraron subcarpetas ni archivos ZIP para procesar.")
                return ""
            
            # Crear carpeta temporal para los resultados
            temp_results_dir = Path.home() / "Downloads" / "resultados_temporales"
            temp_results_dir.mkdir(exist_ok=True)
            
            excel_files = []
            
            # Procesar cada item
            for idx, (item_path, item_name, is_zip) in enumerate(items_to_process, 1):
                if status_callback:
                    status_callback(f"Procesando: {item_name}")
                
                try:
                    # Procesar el item (carpeta o ZIP)
                    result_file = self.process_single_item(item_path, item_name, is_zip, temp_results_dir)
                    if result_file:
                        excel_files.append(result_file)
                    
                    # Actualizar progreso
                    self.current_progress = (idx / self.total_items) * 100
                    if progress_callback:
                        progress_callback(self.current_progress)
                        
                except Exception as e:
                    logger.error(f"Error procesando {item_name}: {e}")
                    if status_callback:
                        status_callback(f"Error en {item_name}: {str(e)}")
            
            # Crear archivo ZIP final
            if excel_files:
                zip_path = self.create_results_zip(excel_files, main_folder_path)
                
                # Limpiar archivos temporales
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
        """Encuentra todas las subcarpetas y archivos ZIP para procesar"""
        items = []
        
        # Buscar subcarpetas
        for item in os.listdir(main_folder_path):
            item_path = os.path.join(main_folder_path, item)
            if os.path.isdir(item_path):
                items.append((item_path, item, False))
        
        # Buscar archivos ZIP
        for item in os.listdir(main_folder_path):
            item_path = os.path.join(main_folder_path, item)
            if os.path.isfile(item_path) and item.lower().endswith('.zip'):
                items.append((item_path, item, True))
        
        return items
    
    def process_single_item(self, item_path: str, item_name: str, is_zip: bool, output_dir: Path) -> str:
        """Procesa un solo item (carpeta o archivo ZIP)"""
        work_folder = item_path
        
        # Si es un archivo ZIP, extraerlo primero
        if is_zip:
            work_folder = self.file_processor.extract_compressed_file(item_path)
        
        try:
            # Buscar archivos PDF
            pdf_files = self.file_processor.find_pdf_files(work_folder)
            
            if not pdf_files:
                logger.warning(f"No se encontraron PDFs en: {item_name}")
                return ""
            
            # Extraer datos de todos los PDFs
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
            
            # Limpiar el nombre del item - REMOVER LA EXTENSIÓN .ZIP si existe
            if is_zip and item_name.lower().endswith('.zip'):
                clean_item_name = self.clean_filename(item_name[:-4])  # Quitar los últimos 4 caracteres (.zip)
            else:
                clean_item_name = self.clean_filename(item_name)
            
            # Exportar a Excel (usar el nombre limpio del item como "ficha")
            excel_path = self.excel_exporter.export_to_excel_massive(
                extracted_data, clean_item_name, output_dir
            )
            
            return excel_path
            
        finally:
            # Limpiar archivos temporales si era un ZIP
            if is_zip:
                self.file_processor.cleanup_temp_files()
    
    def create_results_zip(self, excel_files: List[str], main_folder_path: str) -> str:
        """Crea un archivo ZIP con todos los resultados"""
        zip_path = os.path.join(main_folder_path, "excel_con_resultados.zip")
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for excel_file in excel_files:
                zipf.write(excel_file, os.path.basename(excel_file))
        
        logger.info(f"ZIP creado exitosamente: {zip_path}")
        return zip_path
    
    def cleanup_temp_files(self, temp_dir: Path):
        """Limpia archivos temporales"""
        try:
            for file in temp_dir.glob("*"):
                file.unlink()
            temp_dir.rmdir()
        except Exception as e:
            logger.error(f"Error limpiando archivos temporales: {e}")
    
    def clean_filename(self, filename: str) -> str:
        """Limpia el nombre de archivo para que sea válido"""
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        return filename[:50]  # Limitar longitud