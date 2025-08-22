from Componentes.gui import PDFExtractorGUI
from Componentes.constants import logger
import tkinter.messagebox as messagebox

def main():
    """Función principal"""
    try:
        app = PDFExtractorGUI()
        app.run()
    except Exception as e:
        logger.error(f"Error iniciando la aplicación: {e}")
        messagebox.showerror("Error Fatal", f"Error iniciando la aplicación: {e}")

if __name__ == "__main__":
    main()