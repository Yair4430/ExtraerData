import os, tempfile, shutil, zipfile
from pathlib import Path
from typing import List
from .configuracion import RARFILE_AVAILABLE, logger

class FileProcessor:
    """Clase para procesar archivos y carpetas"""
    
    def __init__(self):
        self.temp_dir = None
    
    def extract_compressed_file(self, file_path: str) -> str:
        """Extrae un archivo comprimido a una carpeta temporal"""
        try:
            # Crear directorio temporal
            self.temp_dir = tempfile.mkdtemp(prefix="pdf_extractor_")
            file_extension = os.path.splitext(file_path)[1].lower()
            
            if file_extension == '.zip':
                with zipfile.ZipFile(file_path, 'r') as zip_ref:
                    # Extraer solo archivos PDF
                    pdf_files = [f for f in zip_ref.namelist() if f.lower().endswith('.pdf')]
                    for pdf_file in pdf_files:
                        zip_ref.extract(pdf_file, self.temp_dir)
                    logger.info(f"Extraídos {len(pdf_files)} archivos PDF del ZIP")
                    
            elif file_extension == '.rar' and RARFILE_AVAILABLE:
                import rarfile
                with rarfile.RarFile(file_path, 'r') as rar_ref:
                    # Extraer solo archivos PDF
                    pdf_files = [f for f in rar_ref.namelist() if f.lower().endswith('.pdf')]
                    for pdf_file in pdf_files:
                        rar_ref.extract(pdf_file, self.temp_dir)
                    logger.info(f"Extraídos {len(pdf_files)} archivos PDF del RAR")
                    
            else:
                raise ValueError(f"Formato de archivo no soportado: {file_extension}")
                
            return self.temp_dir
            
        except Exception as e:
            logger.error(f"Error extrayendo archivo comprimido: {e}")
            if self.temp_dir and os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
                self.temp_dir = None
            raise

    def cleanup_temp_files(self):
        """Limpia los archivos temporales"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir)
                self.temp_dir = None
                logger.info("Archivos temporales limpiados")
            except Exception as e:
                logger.error(f"Error limpiando archivos temporales: {e}")
    
    def find_pdf_files(self, folder_path: str) -> List[str]:
        """Busca archivos PDF recursivamente en una carpeta"""
        pdf_files = []
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.lower().endswith('.pdf'):
                    pdf_files.append(os.path.join(root, file))
        return pdf_files