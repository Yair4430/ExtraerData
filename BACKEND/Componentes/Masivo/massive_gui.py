import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os
from pathlib import Path
from .massive_processor import MassiveProcessor
from ..Normal.constants import logger

class MassiveProcessorGUI:
    """Interfaz gráfica para procesamiento masivo"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Procesamiento Masivo de Documentos")
        self.root.geometry("600x400")
        self.root.resizable(True, True)
        
        # Variables
        self.main_folder_path = ""
        self.processor = MassiveProcessor()
        
        # Configurar estilo
        self.setup_styles()
        self.create_widgets()
        self.center_window()
        
    def setup_styles(self):
        """Configura los estilos de la interfaz"""
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'), foreground='#2c3e50')
        style.configure('Subtitle.TLabel', font=('Arial', 10, 'bold'), foreground='#34495e')
        
    def center_window(self):
        """Centra la ventana en la pantalla"""
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (self.root.winfo_width() // 2)
        y = (self.root.winfo_screenheight() // 2) - (self.root.winfo_height() // 2)
        self.root.geometry(f"+{x}+{y}")
        
    def create_widgets(self):
        """Crea todos los widgets de la interfaz"""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Título
        title_label = ttk.Label(main_frame, text="Procesamiento Masivo de Documentos", style='Title.TLabel')
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Selección de carpeta principal
        ttk.Label(main_frame, text="Carpeta Principal:").grid(row=1, column=0, sticky=tk.W, pady=(0, 10))
        
        self.folder_button = ttk.Button(main_frame, text="Seleccionar Carpeta Principal", command=self.select_main_folder)
        self.folder_button.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.folder_label = ttk.Label(main_frame, text="Ninguna carpeta seleccionada", foreground='gray')
        self.folder_label.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=(0, 20))
        
        # Botón de procesamiento
        self.process_button = ttk.Button(main_frame, text="Iniciar Procesamiento Masivo", command=self.start_massive_processing)
        self.process_button.grid(row=3, column=0, columnspan=2, pady=(0, 20))
        
        # Barra de progreso
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Label de estado
        self.status_label = ttk.Label(main_frame, text="Listo para procesar")
        self.status_label.grid(row=5, column=0, columnspan=2, sticky=tk.W)
        
    def select_main_folder(self):
        """Selecciona la carpeta principal"""
        initial_dir = str(Path.home() / "Downloads")
        
        folder = filedialog.askdirectory(
            title="Seleccione la carpeta principal que contiene las subcarpetas/archivos ZIP",
            initialdir=initial_dir
        )
        if folder:
            self.main_folder_path = folder
            self.folder_label.config(text=f"Carpeta principal: {folder}", foreground='black')
            logger.info(f"Carpeta principal seleccionada: {folder}")
            
    def start_massive_processing(self):
        """Inicia el procesamiento masivo"""
        if not self.main_folder_path:
            messagebox.showerror("Error", "Debe seleccionar una carpeta principal.")
            return
            
        if not os.path.isdir(self.main_folder_path):
            messagebox.showerror("Error", "La carpeta principal seleccionada no existe.")
            return
        
        # Deshabilitar botones durante el procesamiento
        self.process_button.config(state='disabled')
        self.folder_button.config(state='disabled')
        
        # Ejecutar en hilo separado
        thread = threading.Thread(target=self.run_massive_processing)
        thread.daemon = True
        thread.start()
        
    def run_massive_processing(self):
        """Ejecuta el procesamiento masivo en un hilo separado"""
        try:
            zip_path = self.processor.process_massive(
                self.main_folder_path,
                progress_callback=self.update_progress,
                status_callback=self.update_status
            )
            
            if zip_path:
                messagebox.showinfo("Éxito", f"Procesamiento masivo completado.\nZIP creado en: {zip_path}")
            else:
                messagebox.showwarning("Aviso", "Procesamiento completado pero no se generaron resultados.")
                
        except Exception as e:
            logger.error(f"Error en procesamiento masivo: {e}")
            messagebox.showerror("Error", f"Error durante el procesamiento masivo: {e}")
        finally:
            # Rehabilitar botones
            self.root.after(0, lambda: self.process_button.config(state='normal'))
            self.root.after(0, lambda: self.folder_button.config(state='normal'))
            self.root.after(0, lambda: self.status_label.config(text="Procesamiento finalizado"))
    
    def update_progress(self, progress: float):
        """Actualiza la barra de progreso"""
        self.root.after(0, lambda: self.progress_var.set(progress))
    
    def update_status(self, message: str):
        """Actualiza el mensaje de estado"""
        self.root.after(0, lambda: self.status_label.config(text=message))
    
    def run(self):
        """Ejecuta la aplicación"""
        self.root.mainloop()