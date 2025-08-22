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
            # Determinar el tipo de documento (CC o TI)
            tipo_documento = self.determinar_tipo_documento(text)
            
            # Patrones de búsqueda según el tipo de documento
            if tipo_documento == 'CC':
                return self.extract_data_cc(text, filename)
            elif tipo_documento == 'TI':
                return self.extract_data_ti(text, filename)
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error extrayendo datos del documento: {e}")
            return None
    
    def determinar_tipo_documento(self, text: str) -> str:
        """Determina si el documento es CC o TI basado en el contenido del texto"""
        if re.search(r'C[eé]dula de Ciudadan[ií]a', text, re.IGNORECASE):
            return 'CC'
        elif re.search(r'Número Único de Identificación Personal', text, re.IGNORECASE):
            return 'TI'
        else:
            return 'DESCONOCIDO'
    
    def extract_data_cc(self, text: str, filename: str) -> Optional[DocumentoData]:
        """Extrae datos de cédulas de ciudadanía"""
        try:
            # Patrones de búsqueda para CC
            cedula_match = re.search(r'C[eé]dula de Ciudadan[ií]a:\s*([\d\.]+)', text)
            fecha_match = re.search(r'Fecha de Expedici[oó]n:\s*(\d{1,2})\s+DE\s+([A-Z]+)\s+DE\s+(\d{4})', text, re.IGNORECASE)
            vigencia_match = re.search(r'válida en todo el territorio nacional hasta el (\d{1,2}) de ([A-Za-z]+) de (\d{4})', text, re.IGNORECASE)
            
            # Extraer nombres y apellidos
            nombres_apellidos_match = re.search(r'A nombre de:\s*([A-ZÁÉÍÓÚÑ\s]+?)(?=\n|Estado|$)', text, re.IGNORECASE)
            
            if not cedula_match or not fecha_match or not vigencia_match:
                return None
                
            cedula = cedula_match.group(1).replace('.', '')
            dia, mes, anio = fecha_match.group(1), fecha_match.group(2).capitalize(), fecha_match.group(3)
            
            # Obtener nombres y apellidos
            nombres_apellidos = "N/A"
            if nombres_apellidos_match:
                nombres_apellidos = nombres_apellidos_match.group(1).strip()
                
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
            logger.error(f"Error extrayendo datos de CC: {e}")
            return None
    
    def extract_data_ti(self, text: str, filename: str) -> Optional[DocumentoData]:
        """Extrae datos de tarjetas de identidad"""
        try:
            # Patrones de búsqueda para TI
            numero_match = re.search(r'Número Único de Identificación Personal\s+(\d+)', text, re.IGNORECASE)
            fecha_match = re.search(r'el\s+(\d{1,2})\s+DE\s+([A-Z]+)\s+DE\s+(\d{4})', text, re.IGNORECASE)
            
            # NUEVO PATRÓN MEJORADO para nombres
            nombres_match = re.search(r'certifica que una vez consultado.*?,\s+([A-ZÁÉÍÓÚÑ\s]+)\s+tiene inscrito', text, re.IGNORECASE | re.DOTALL)
            
            if not numero_match or not fecha_match:
                return None
                
            numero_documento = numero_match.group(1)
            dia, mes, anio = fecha_match.group(1), fecha_match.group(2).capitalize(), fecha_match.group(3)
            
            # Obtener nombres y apellidos
            nombres_apellidos = "N/A"
            if nombres_match:
                nombres_apellidos = nombres_match.group(1).strip()
                # Limpiar posibles espacios extras
                nombres_apellidos = ' '.join(nombres_apellidos.split())
            
            # Para TI, no hay fecha de vigencia específica - CAMBIO AQUÍ
            # Usar "N/A" para días restantes en lugar de un cálculo
            fecha_vigencia = None  # No aplica para TI
            dias_restantes = "N/A"  # Cambiado de número a string "N/A"
            estado = 'VIGENTE'  # Las TI generalmente no vencen
            
            return DocumentoData(
                tipo_documento='TI',
                numero_documento=numero_documento,
                nombres_apellidos=nombres_apellidos,
                dia=dia,
                mes=mes,
                año=anio,
                fecha_vigencia=fecha_vigencia,  # None para TI
                dias_restantes=dias_restantes,  # "N/A" para TI
                estado=estado,
                archivo_origen=filename
            )
            
        except Exception as e:
            logger.error(f"Error extrayendo datos de TI: {e}")
            return None