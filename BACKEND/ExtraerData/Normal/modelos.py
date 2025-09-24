from dataclasses import dataclass
from datetime import datetime
from typing import Union

@dataclass
class DocumentoData:
    # Define la estructura de datos para almacenar información extraída de documentos PDF
    # Esta clase representa los datos fundamentales de cualquier documento de identidad procesado
    
    tipo_documento: str           # Tipo de documento: CC, TI, PPT, CE
    numero_documento: str         # Número único del documento de identidad
    nombres_apellidos: str        # Nombre completo del titular del documento
    dia: str                      # Día de expedición del documento
    mes: str                      # Mes de expedición del documento (en texto)
    año: str                      # Año de expedición del documento
    fecha_vigencia: datetime      # Fecha de vencimiento del documento (objeto datetime)
    dias_restantes: Union[int, str]  # Días restantes para vencimiento (número o "N/A" si no aplica)
    estado: str                   # Estado del documento: EXTRAÍDO, VIGENTE, PRÓXIMO A VENCER, etc.
    archivo_origen: str           # Nombre del archivo PDF del que se extrajeron los datos