import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os
from pathlib import Path
from Componentes.Masivo.massive_processor import MassiveProcessor
from Componentes.Normal.constants import logger
from Componentes.Normal.gui import PDFExtractorGUI

class MassiveProcessorGUI:
    """Interfaz gráfica para procesamiento masivo"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Procesamiento Masivo de Documentos")
        self.root.geometry("700x480")
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
        style.theme_use("clam")

        # Colores base
        self.bg_color = "#1E1E2E"
        self.card_color = "#2E2E3E"
        self.btn_color = "#3B82F6"
        self.btn_hover = "#2563EB"
        self.text_color = "#FFFFFF"
        self.subtitle_color = "#9CA3AF"

        self.root.configure(bg=self.bg_color)

        # Estilos
        style.configure("Title.TLabel",
                        font=("Segoe UI Semibold", 18),
                        foreground=self.text_color,
                        background=self.card_color)

        style.configure("Subtitle.TLabel",
                        font=("Segoe UI", 11),
                        foreground=self.subtitle_color,
                        background=self.card_color)

        style.configure("Status.TLabel",
                        font=("Segoe UI", 10, "italic"),
                        foreground=self.text_color,
                        background=self.card_color)

        style.configure("Custom.TButton",
                        font=("Segoe UI", 11, "bold"),
                        padding=10,
                        relief="flat",
                        background=self.btn_color,
                        foreground=self.text_color)
        style.map("Custom.TButton",
                  background=[("active", self.btn_hover)],
                  foreground=[("active", self.text_color)])

        style.configure("Custom.Horizontal.TProgressbar",
                        troughcolor=self.card_color,
                        bordercolor=self.card_color,
                        background=self.btn_color,
                        lightcolor=self.btn_hover,
                        darkcolor=self.btn_hover)

    def center_window(self):
        """Centra la ventana en la pantalla"""
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (self.root.winfo_width() // 2)
        y = (self.root.winfo_screenheight() // 2) - (self.root.winfo_height() // 2)
        self.root.geometry(f"+{x}+{y}")

    def create_widgets(self):
        """Crea todos los widgets de la interfaz"""
        main_frame = tk.Frame(self.root, bg=self.card_color, bd=0, relief="flat")
        main_frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.85, relheight=0.85)

        title_label = ttk.Label(main_frame, text="Procesamiento Masivo de Documentos", style="Title.TLabel")
        title_label.pack(pady=(20, 5))

        subtitle_label = ttk.Label(main_frame, text="Seleccione la carpeta principal y ejecute el procesamiento", style="Subtitle.TLabel")
        subtitle_label.pack(pady=(0, 25))

        self.folder_button = ttk.Button(main_frame, text="📂 Seleccionar Carpeta Principal",
                                        style="Custom.TButton", command=self.select_main_folder)
        self.folder_button.pack(pady=10, fill=tk.X, padx=40)

        self.folder_label = ttk.Label(main_frame, text="Ninguna carpeta seleccionada",
                                      style="Subtitle.TLabel", anchor="center")
        self.folder_label.pack(pady=(5, 25))

        self.process_button = ttk.Button(main_frame, text="⚙️ Iniciar Procesamiento Masivo",
                                         style="Custom.TButton", command=self.start_massive_processing)
        self.process_button.pack(pady=10, fill=tk.X, padx=40)

        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var,
                                            maximum=100, style="Custom.Horizontal.TProgressbar")
        self.progress_bar.pack(fill=tk.X, padx=40, pady=(25, 10))

        self.status_label = ttk.Label(main_frame, text="🔹 Listo para procesar", style="Status.TLabel")
        self.status_label.pack(pady=(5, 20), anchor="w", padx=20)

        # Botón volver al menú principal
        self.back_button = ttk.Button(main_frame, text="🏠 Volver al Menú Principal",
                                      style="Custom.TButton", command=self.back_to_menu)
        self.back_button.pack(pady=(10, 5), fill=tk.X, padx=40)

    def select_main_folder(self):
        initial_dir = str(Path.home() / "Downloads")
        folder = filedialog.askdirectory(
            title="Seleccione la carpeta principal que contiene las subcarpetas/archivos ZIP",
            initialdir=initial_dir
        )
        if folder:
            self.main_folder_path = folder
            self.folder_label.config(text=f"📁 Carpeta: {folder}", foreground=self.text_color)
            logger.info(f"Carpeta principal seleccionada: {folder}")

    def start_massive_processing(self):
        if not self.main_folder_path:
            messagebox.showerror("Error", "Debe seleccionar una carpeta principal.")
            return

        if not os.path.isdir(self.main_folder_path):
            messagebox.showerror("Error", "La carpeta principal seleccionada no existe.")
            return

        self.process_button.config(state="disabled")
        self.folder_button.config(state="disabled")

        thread = threading.Thread(target=self.run_massive_processing)
        thread.daemon = True
        thread.start()

    def run_massive_processing(self):
        try:
            zip_path = self.processor.process_massive(
                self.main_folder_path,
                progress_callback=self.update_progress,
                status_callback=self.update_status
            )

            if zip_path:
                messagebox.showinfo("Éxito", f"Procesamiento masivo completado.\nZIP creado en: {zip_path}")
                self.reset_ui()  # 🔹 limpiar después de la alerta
            else:
                messagebox.showwarning("Aviso", "Procesamiento completado pero no se generaron resultados.")
                self.reset_ui()

        except Exception as e:
            logger.error(f"Error en procesamiento masivo: {e}")
            messagebox.showerror("Error", f"Error durante el procesamiento masivo: {e}")
        finally:
            self.root.after(0, lambda: self.process_button.config(state="normal"))
            self.root.after(0, lambda: self.folder_button.config(state="normal"))
            self.root.after(0, lambda: self.status_label.config(text="✅ Procesamiento finalizado"))

    def reset_ui(self):
        """Limpia la interfaz después del procesamiento"""
        self.root.after(0, lambda: self.folder_label.config(text="Ninguna carpeta seleccionada", foreground=self.subtitle_color))
        self.root.after(0, lambda: self.progress_var.set(0))
        self.root.after(0, lambda: self.status_label.config(text="🔹 Listo para procesar"))
        self.main_folder_path = ""

    def update_progress(self, progress: float):
        self.root.after(0, lambda: self.progress_var.set(progress))

    def update_status(self, message: str):
        self.root.after(0, lambda: self.status_label.config(text=f"🔄 {message}"))

    def back_to_menu(self):
        """Cerrar ventana y volver al menú principal"""
        self.root.destroy()
        from contenedor import contenedor  
        contenedor()  # 🔹 Regresa al selector de modo

    def run(self):
        self.root.mainloop()
