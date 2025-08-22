from dataclasses import dataclass
from datetime import datetime

@dataclass
class DocumentoData:
    """Clase para representar los datos de un documento"""
    tipo_documento: str
    numero_documento: str
    nombres_apellidos: str
    dia: str
    mes: str
    año: str
    fecha_vigencia: datetime
    dias_restantes: int
    estado: str
    archivo_origen: str