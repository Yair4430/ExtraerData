import logging, sys

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pdf_extractor.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('pdf_extractor')

# Constantes
MESES = { 'Enero': 1, 'Febrero': 2, 'Marzo': 3, 'Abril': 4, 'Mayo': 5, 'Junio': 6, 'Julio': 7, 'Agosto': 8, 'Septiembre': 9, 'Octubre': 10, 'Noviembre': 11, 'Diciembre': 12}

DIAS_ALERTA_VENCIMIENTO = 30  # Días antes del vencimiento para alertar

# Try to import rarfile (optional dependency)
try:
    import rarfile
    RARFILE_AVAILABLE = True
except ImportError:
    RARFILE_AVAILABLE = False
    logging.warning("rarfile no está disponible. Solo se soportarán archivos ZIP.")