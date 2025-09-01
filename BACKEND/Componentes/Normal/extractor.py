import re
from datetime import datetime, timedelta
from typing import Optional
from .modelos import DocumentoData
from .configuracion import MESES, DIAS_ALERTA_VENCIMIENTO, logger

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
            # Determinar el tipo de documento (CC, TI, PPT o CE)
            tipo_documento = self.determinar_tipo_documento(text)
            
            # Patrones de búsqueda según el tipo de documento
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
        """Determina si el documento es CC, TI, PPT o CE basado en el contenido del texto"""
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
            
            # Obtener nombres and apellidos
            nombres_apellidos = "N/A"
            if nombres_match:
                nombres_apellidos = nombres_match.group(1).strip()
                # Limpiar posibles espacios extras
                nombres_apellidos = ' '.join(nombres_apellidos.split())
            
            # Para TI, no hay fecha de vigencia específica
            fecha_vigencia = None
            dias_restantes = "N/A"
            estado = 'VIGENTE'
            
            return DocumentoData(
                tipo_documento='TI',
                numero_documento=numero_documento,
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
            logger.error(f"Error extrayendo datos de TI: {e}")
            return None

    def extract_data_ppt(self, text: str, filename: str) -> Optional[DocumentoData]:
        """Extrae datos de Permisos Por Protección Temporal (PPT)"""
        try:
            # Patrones de búsqueda para PPT
            numero_match = re.search(r'(?:PPT|RUMV)\s+(?:número|numero)?\s*[:]?\s*(\d+)', text, re.IGNORECASE)
            fecha_match = re.search(r'a los\s+(\d{1,2})\s+días del mes de\s+([A-Za-z]+)\s+de\s+(\d{4})', text, re.IGNORECASE)
            nombres_match = re.search(r'el migrante venezolano\s+([A-ZÁÉÍÓÚÑ\s]+?)\s+surtió', text, re.IGNORECASE)
            
            if not numero_match or not fecha_match:
                return None
                
            numero_documento = numero_match.group(1)
            dia, mes, anio = fecha_match.group(1), fecha_match.group(2).capitalize(), fecha_match.group(3)
            
            # Obtener nombres y apellidos
            nombres_apellidos = "N/A"
            if nombres_match:
                nombres_apellidos = nombres_match.group(1).strip()
            
            # Calcular fecha de vigencia (30 días después de la expedición)
            fecha_expedicion = datetime(int(anio), MESES.get(mes, 1), int(dia))
            fecha_vigencia = fecha_expedicion + timedelta(days=30)
            
            # Calcular días restantes y estado
            dias_restantes = (fecha_vigencia - datetime.now()).days
            
            if dias_restantes < 0:
                estado = 'VENCIDO'
            elif dias_restantes <= DIAS_ALERTA_VENCIMIENTO:
                estado = 'POR VENCER'
            else:
                estado = 'VIGENTE'
            
            return DocumentoData(
                tipo_documento='PPT',
                numero_documento=numero_documento,
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
            logger.error(f"Error extrayendo datos de PPT: {e}")
            return None

    def extract_data_ce(self, text: str, filename: str) -> Optional[DocumentoData]:
        """Extrae datos de Cédulas de Extranjería (CE)"""
        try:
            # Patrones de búsqueda para CE
            cedula_match = re.search(r'C[eé]dula de Extranjer[ií]a:\s*(\d+)', text, re.IGNORECASE)
            fecha_expedicion_match = re.search(r'Fecha de Expedici[oó]n:\s*(\d{4})/(\d{2})/(\d{2})', text, re.IGNORECASE)
            fecha_vencimiento_match = re.search(r'Fecha de Vencimiento\s*(\d{4})/(\d{2})/(\d{2})', text, re.IGNORECASE)
            nombres_match = re.search(r'Nombres y Apellidos\s+([A-ZÁÉÍÓÚÑ\s]+)(?=\n|Fecha de Nacimiento)', text, re.IGNORECASE)
            
            if not cedula_match or not fecha_expedicion_match:
                return None
                
            cedula = cedula_match.group(1)
            
            # Extraer fecha de expedición (año, mes, día)
            anio_exp, mes_exp, dia_exp = fecha_expedicion_match.group(1), fecha_expedicion_match.group(2), fecha_expedicion_match.group(3)
            dia, mes, anio = dia_exp, self.get_nombre_mes(int(mes_exp)), anio_exp
            
            # Obtener nombres y apellidos
            nombres_apellidos = "N/A"
            if nombres_match:
                nombres_apellidos = nombres_match.group(1).strip()
            
            # Calcular fecha de vigencia (30 días después de la expedición del certificado)
            fecha_expedicion_cert = datetime.now()  # La fecha de expedición del certificado es la fecha actual
            fecha_vigencia = fecha_expedicion_cert + timedelta(days=30)
            
            # Calcular días restantes y estado
            dias_restantes = (fecha_vigencia - datetime.now()).days
            
            if dias_restantes < 0:
                estado = 'VENCIDO'
            elif dias_restantes <= DIAS_ALERTA_VENCIMIENTO:
                estado = 'POR VENCER'
            else:
                estado = 'VIGENTE'
            
            return DocumentoData(
                tipo_documento='CE',
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
            logger.error(f"Error extrayendo datos de CE: {e}")
            return None

    def get_nombre_mes(self, numero_mes: int) -> str:
        """Convierte un número de mes a su nombre correspondiente"""
        meses = {
            1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril', 5: 'Mayo', 6: 'Junio',
            7: 'Julio', 8: 'Agosto', 9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
        }
        return meses.get(numero_mes, 'Enero')