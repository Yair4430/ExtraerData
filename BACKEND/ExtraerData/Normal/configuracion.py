import logging, sys

# Configuración del sistema de logging para registrar eventos y errores
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pdf_extractor.log'),  # Guarda logs en archivo
        logging.StreamHandler(sys.stdout)          # Muestra logs en consola
    ]
)
logger = logging.getLogger('pdf_extractor')

# Diccionario de mapeo de nombres de meses a números (para procesamiento de fechas)
MESES = { 'Enero': 1, 'Febrero': 2, 'Marzo': 3, 'Abril': 4, 'Mayo': 5, 'Junio': 6, 
         'Julio': 7, 'Agosto': 8, 'Septiembre': 9, 'Octubre': 10, 'Noviembre': 11, 'Diciembre': 12}

# Constante que define los días de anticipación para alertas de vencimiento
DIAS_ALERTA_VENCIMIENTO = 30  

# Verifica si la librería rarfile está disponible para soportar archivos RAR
try:
    import rarfile
    RARFILE_AVAILABLE = True
except ImportError:
    RARFILE_AVAILABLE = False
    logging.warning("rarfile no está disponible. Solo se soportarán archivos ZIP.")