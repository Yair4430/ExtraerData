import re
from datetime import datetime
from typing import Optional
from .data_models import DocumentoData
from .constants import MESES, DIAS_ALERTA_VENCIMIENTO, logger

class DocumentExtractor:
    """Clase para extraer datos de documentos desde texto PDF"""
    
    def __init__(self):
        pass
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extrae texto de un archivo PDF"""
        import pdfplumber
        text = ''
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + '\n'
        return text
        
    def extract_document_data(self, text: str, filename: str) -> Optional[DocumentoData]:
        """Extrae los datos del documento desde el texto"""
        try:
            # Patrones de búsqueda mejorados
            cedula_match = re.search(r'C[eé]dula de Ciudadan[ií]a:\s*([\d\.]+)', text)
            fecha_match = re.search(r'Fecha de Expedici[oó]n:\s*(\d{1,2})\s+DE\s+([A-Z]+)\s+DE\s+(\d{4})', text, re.IGNORECASE)
            vigencia_match = re.search(r'válida en todo el territorio nacional hasta el (\d{1,2}) de ([A-Za-z]+) de (\d{4})', text, re.IGNORECASE)
            
            # Intentar extraer nombres (patrón común en cédulas)
            nombres_match = re.search(r'Nombres:\s*([A-ZÁÉÍÓÚÑ\s]+)', text) or re.search(r'NOMBRES:\s*([A-ZÁÉÍÓÚÑ\s]+)', text)
            apellidos_match = re.search(r'Apellidos:\s*([A-ZÁÉÍÓÚÑ\s]+)', text) or re.search(r'APELLIDOS:\s*([A-ZÁÉÍÓÚÑ\s]+)', text)
            
            if not cedula_match or not fecha_match or not vigencia_match:
                return None
                
            cedula = cedula_match.group(1).replace('.', '')
            dia, mes, anio = fecha_match.group(1), fecha_match.group(2).capitalize(), fecha_match.group(3)
            
            # Construir nombre completo
            nombres_apellidos = "N/A"
            if nombres_match and apellidos_match:
                nombres = nombres_match.group(1).strip()
                apellidos = apellidos_match.group(1).strip()
                nombres_apellidos = f"{nombres} {apellidos}"
            elif nombres_match:
                nombres_apellidos = nombres_match.group(1).strip()
                
            # Fecha de vigencia
            dia_v, mes_v, anio_v = vigencia_match.group(1), vigencia_match.group(2).capitalize(), vigencia_match.group(3)
            fecha_vigencia = datetime(int(anio_v), MESES.get(mes_v, 1), int(dia_v))
            
            # Calcular días restantes y estado
            dias_restantes = (fecha_vigencia - datetime.now()).days
            
            if dias_restantes < 0:
                estado = 'VENCIDO'
            elif dias_restantes <= DIAS_ALERTA_VENCIMIENTO:
                estado = 'POR VENCER'
            else:
                estado = 'VIGENTE'
                
            return DocumentoData(
                tipo_documento='CC',
                numero_documento=cedula,
                nombres_apellidos=nombres_apellidos,
                dia=dia,
                mes=mes,
                año=anio,
                fecha_vigencia=fecha_vigencia,
                dias_restantes=dias_restantes,
                estado=estado,
                archivo_origen=filename
            )
            
        except Exception as e:
            logger.error(f"Error extrayendo datos del documento: {e}")
            return None