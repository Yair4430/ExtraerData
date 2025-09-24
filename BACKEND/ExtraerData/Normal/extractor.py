import re
from datetime import datetime
from typing import Optional
from .Modelos import DocumentoData
from .Configuracion import MESES, logger

class DocumentExtractor:
    
    def __init__(self):
        # Inicializa el extractor de documentos sin configuración específica
        pass
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        # Extrae texto de un archivo PDF usando pdfplumber, página por página
        import pdfplumber
        text = ''
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + '\n'
        return text
        
    def extract_document_data(self, text: str, filename: str) -> Optional[DocumentoData]:
        # Función principal que coordina la extracción de datos según el tipo de documento detectado
        try:
            # Identifica el tipo de documento (CC, TI, PPT o CE) mediante patrones de texto
            tipo_documento = self.determinar_tipo_documento(text)
            
            # Llama a la función específica según el tipo de documento detectado
            if tipo_documento == 'CC':
                return self.extract_data_cc(text, filename)
            elif tipo_documento == 'TI':
                return self.extract_data_ti(text, filename)
            elif tipo_documento == 'PPT':
                return self.extract_data_ppt(text, filename)
            elif tipo_documento == 'CE':
                return self.extract_data_ce(text, filename)
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error extrayendo datos del documento: {e}")
            return None
    
    def determinar_tipo_documento(self, text: str) -> str:
        # Detecta el tipo de documento analizando patrones de texto específicos
        if re.search(r'C[eé]dula de Ciudadan[ií]a', text, re.IGNORECASE):
            return 'CC'
        elif re.search(r'Número Único de Identificación Personal', text, re.IGNORECASE):
            return 'TI'
        elif re.search(r'Permiso Por Protección Temporal|PPT|RUMV', text, re.IGNORECASE):
            return 'PPT'
        elif re.search(r'C[eé]dula de Extranjer[ií]a', text, re.IGNORECASE):
            return 'CE'
        else:
            return 'DESCONOCIDO'
    
    def extract_data_cc(self, text: str, filename: str) -> Optional[DocumentoData]:
        # Extrae datos específicos de Cédula de Ciudadanía colombiana
        try:
            # Patrones de expresión regular para cédula, fecha de expedición y vigencia
            cedula_match = re.search(r'C[eé]dula de Ciudadan[ií]a:\s*([\d\.]+)', text)
            fecha_match = re.search(r'Fecha de Expedici[oó]n:\s*(\d{1,2})\s+DE\s+([A-Z]+)\s+DE\s+(\d{4})', text, re.IGNORECASE)
            vigencia_match = re.search(r'válida en todo el territorio nacional hasta el (\d{1,2}) de ([A-Za-z]+) de (\d{4})', text, re.IGNORECASE)
            
            # Extrae nombres y apellidos del titular
            nombres_apellidos_match = re.search(r'A nombre de:\s*([A-ZÁÉÍÓÚÑ\s]+?)(?=\n|Estado|$)', text, re.IGNORECASE)
            
            if not cedula_match or not fecha_match or not vigencia_match:
                return None
                
            # Limpia y formatea los datos extraídos
            cedula = cedula_match.group(1).replace('.', '')
            dia, mes, anio = fecha_match.group(1), fecha_match.group(2).capitalize(), fecha_match.group(3)
            
            # Procesa nombres y apellidos
            nombres_apellidos = "N/A"
            if nombres_apellidos_match:
                nombres_apellidos = nombres_apellidos_match.group(1).strip()
                
            # Calcula fecha de vigencia usando el diccionario de meses
            dia_v, mes_v, anio_v = vigencia_match.group(1), vigencia_match.group(2).capitalize(), vigencia_match.group(3)
            fecha_vigencia = datetime(int(anio_v), MESES.get(mes_v, 1), int(dia_v))
            
            estado = 'EXTRAÍDO'
                
            return DocumentoData(tipo_documento='CC', numero_documento=cedula, nombres_apellidos=nombres_apellidos, dia=dia, mes=mes, año=anio, fecha_vigencia=fecha_vigencia, dias_restantes="N/A", estado=estado, archivo_origen=filename )
            
        except Exception as e:
            logger.error(f"Error extrayendo datos de CC: {e}")
            return None
    
    def extract_data_ti(self, text: str, filename: str) -> Optional[DocumentoData]:
        # Extrae datos de Tarjeta de Identidad colombiana
        try:
            # Patrones para número de documento y fecha de expedición
            numero_match = re.search(r'Número Único de Identificación Personal\s+(\d+)', text, re.IGNORECASE)
            fecha_match = re.search(r'el\s+(\d{1,2})\s+DE\s+([A-Z]+)\s+DE\s+(\d{4})', text, re.IGNORECASE)
            
            # Patrón mejorado para extraer nombres del titular
            nombres_match = re.search(r'certifica que una vez consultado.*?,\s+([A-ZÁÉÍÓÚÑ\s]+)\s+tiene inscrito', text, re.IGNORECASE | re.DOTALL)
            
            if not numero_match or not fecha_match:
                return None
                
            numero_documento = numero_match.group(1)
            dia, mes, anio = fecha_match.group(1), fecha_match.group(2).capitalize(), fecha_match.group(3)
            
            # Procesa y limpia nombres y apellidos
            nombres_apellidos = "N/A"
            if nombres_match:
                nombres_apellidos = nombres_match.group(1).strip()
                nombres_apellidos = ' '.join(nombres_apellidos.split())
            
            fecha_vigencia = None
            estado = 'EXTRAÍDO'
            
            return DocumentoData(tipo_documento='TI', numero_documento=numero_documento, nombres_apellidos=nombres_apellidos, dia=dia, mes=mes, año=anio, fecha_vigencia=fecha_vigencia, dias_restantes="N/A", estado=estado, archivo_origen=filename )
            
        except Exception as e:
            logger.error(f"Error extrayendo datos de TI: {e}")
            return None

    def extract_data_ppt(self, text: str, filename: str) -> Optional[DocumentoData]:
        # Extrae datos de Permiso por Protección Temporal (migrantes venezolanos)
        try:
            # Patrones para número PPT/RUMV, fecha de expedición y nombres
            numero_match = re.search(r'(?:PPT|RUMV)\s+(?:número|numero)?\s*[:]?\s*(\d+)', text, re.IGNORECASE)
            fecha_match = re.search(r'a los\s+(\d{1,2})\s+días del mes de\s+([A-Za-z]+)\s+de\s+(\d{4})', text, re.IGNORECASE)
            nombres_match = re.search(r'el migrante venezolano\s+([A-ZÁÉÍÓÚÑ\s]+?)\s+surtió', text, re.IGNORECASE)
            
            if not numero_match or not fecha_match:
                return None
                
            numero_documento = numero_match.group(1)
            dia, mes, anio = fecha_match.group(1), fecha_match.group(2).capitalize(), fecha_match.group(3)
            
            nombres_apellidos = "N/A"
            if nombres_match:
                nombres_apellidos = nombres_match.group(1).strip()
            
            fecha_vigencia = None
            estado = 'EXTRAÍDO'
            
            return DocumentoData(tipo_documento='PPT', numero_documento=numero_documento, nombres_apellidos=nombres_apellidos, dia=dia, mes=mes, año=anio, fecha_vigencia=fecha_vigencia, dias_restantes="N/A",estado=estado, archivo_origen=filename)
            
        except Exception as e:
            logger.error(f"Error extrayendo datos de PPT: {e}")
            return None

    def extract_data_ce(self, text: str, filename: str) -> Optional[DocumentoData]:
        # Extrae datos de Cédula de Extranjería
        try:
            # Patrones para número de cédula, fecha de expedición y nombres
            cedula_match = re.search(r'C[eé]dula de Extranjer[ií]a:\s*(\d+)', text, re.IGNORECASE)
            fecha_expedicion_match = re.search(r'Fecha de Expedici[oó]n:\s*(\d{4})/(\d{2})/(\d{2})', text, re.IGNORECASE)
            nombres_match = re.search(r'Nombres y Apellidos\s+([A-ZÁÉÍÓÚÑ\s]+)(?=\n|Fecha de Nacimiento)', text, re.IGNORECASE)
            
            if not cedula_match or not fecha_expedicion_match:
                return None
                
            cedula = cedula_match.group(1)
            
            # Convierte fecha numérica a formato legible (YYYY/MM/DD -> día, mes_nombre, año)
            anio_exp, mes_exp, dia_exp = fecha_expedicion_match.group(1), fecha_expedicion_match.group(2), fecha_expedicion_match.group(3)
            dia, mes, anio = dia_exp, self.get_nombre_mes(int(mes_exp)), anio_exp
            
            nombres_apellidos = "N/A"
            if nombres_match:
                nombres_apellidos = nombres_match.group(1).strip()
            
            fecha_vigencia = None
            estado = 'EXTRAÍDO'
            
            return DocumentoData(tipo_documento='CE', numero_documento=cedula, nombres_apellidos=nombres_apellidos, dia=dia, mes=mes, año=anio, fecha_vigencia=fecha_vigencia, dias_restantes="N/A", estado=estado, archivo_origen=filename)
            
        except Exception as e:
            logger.error(f"Error extrayendo datos de CE: {e}")
            return None

    def get_nombre_mes(self, numero_mes: int) -> str:
        # Convierte número de mes (1-12) a nombre del mes en español en mayúsculas
        meses = {
            1: 'ENERO', 2: 'FEBRERO', 3: 'MARZO', 4: 'ABRIL', 5: 'MAYO', 6: 'JUNIO', 
            7: 'JULIO', 8: 'AGOSTO', 9: 'SEPTIEMBRE', 10: 'OCTUBRE', 11: 'NOVIEMBRE', 12: 'DICIEMBRE'}
        return meses.get(numero_mes, 'ENERO')