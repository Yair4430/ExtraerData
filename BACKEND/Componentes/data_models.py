from dataclasses import dataclass
from datetime import datetime
from typing import Union

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
    dias_restantes: Union[int, str]  # Puede ser int o string "N/A"
    estado: str
    archivo_origen: str