from Componentes.Normal.gui import PDFExtractorGUI
from Componentes.Masivo.massive_gui import MassiveProcessorGUI
from Componentes.Normal.constants import logger
import tkinter as tk
from tkinter import ttk, messagebox

def contenedor():
    """Función principal con selector de modo"""
    try:
        # Crear ventana de selección de modo
        mode_window = tk.Tk()
        mode_window.title("Selector de Modo")
        mode_window.geometry("400x200")
        mode_window.resizable(False, False)
        
        # Centrar ventana
        mode_window.update_idletasks()
        x = (mode_window.winfo_screenwidth() // 2) - (mode_window.winfo_width() // 2)
        y = (mode_window.winfo_screenheight() // 2) - (mode_window.winfo_height() // 2)
        mode_window.geometry(f"+{x}+{y}")
        
        # Frame principal
        main_frame = ttk.Frame(mode_window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title_label = ttk.Label(main_frame, text="Seleccione el modo de operación", font=('Arial', 14, 'bold'))
        title_label.pack(pady=(0, 30))
        
        # Botones de modo
        single_mode_btn = ttk.Button(main_frame, text="Modo Individual", 
                                   command=lambda: launch_single_mode(mode_window))
        single_mode_btn.pack(pady=10, fill=tk.X)
        
        massive_mode_btn = ttk.Button(main_frame, text="Modo Masivo", 
                                    command=lambda: launch_massive_mode(mode_window))
        massive_mode_btn.pack(pady=10, fill=tk.X)
        
        def launch_single_mode(window):
            window.destroy()
            app = PDFExtractorGUI()
            app.run()
        
        def launch_massive_mode(window):
            window.destroy()
            app = MassiveProcessorGUI()
            app.run()
        
        mode_window.mainloop()
        
    except Exception as e:
        logger.error(f"Error iniciando la aplicación: {e}")
        messagebox.showerror("Error Fatal", f"Error iniciando la aplicación: {e}")
