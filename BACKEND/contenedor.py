from Componentes.Normal.gui import PDFExtractorGUI
from Componentes.Masivo.massive_gui import MassiveProcessorGUI
from Componentes.Normal.constants import logger
import tkinter as tk
from tkinter import ttk, messagebox

def contenedor():
    """Función principal con selector de modo"""
    try:
        # Crear ventana principal
        mode_window = tk.Tk()
        mode_window.title("Selector de Modo")
        mode_window.geometry("650x400")  # 🔹 Ventana más grande
        mode_window.resizable(True, True)  # 🔹 Ahora se puede redimensionar

        # ===== COLORES =====
        bg_color = "#1E1E2E"       # Fondo oscuro
        card_color = "#2E2E3E"     # Panel central
        btn_color = "#3B82F6"      # Azul primario
        btn_hover = "#2563EB"      # Azul más oscuro
        text_color = "#FFFFFF"     # Texto blanco
        subtitle_color = "#9CA3AF" # Gris claro

        mode_window.configure(bg=bg_color)

        # ===== ESTILOS DE BOTONES =====
        style = ttk.Style()
        style.theme_use("clam")

        style.configure("Custom.TButton",
                        font=("Segoe UI", 12, "bold"),
                        padding=12,
                        relief="flat",
                        background=btn_color,
                        foreground=text_color)

        style.map("Custom.TButton",
                  background=[("active", btn_hover)],
                  foreground=[("active", text_color)])

        # ===== FRAME PRINCIPAL =====
        main_frame = tk.Frame(mode_window, bg=card_color, bd=0, relief="flat")
        main_frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.8, relheight=0.7)
        # 🔹 Usa proporciones relativas para adaptarse al redimensionamiento

        # ===== TÍTULO =====
        title_label = tk.Label(main_frame, text="Seleccione el modo de operación",
                               font=('Segoe UI Semibold', 18), bg=card_color, fg=text_color)
        title_label.pack(pady=(20, 5))

        subtitle_label = tk.Label(main_frame, text="Elija entre análisis individual o procesamiento masivo",
                                  font=('Segoe UI', 11), bg=card_color, fg=subtitle_color)
        subtitle_label.pack(pady=(0, 20))

        # ===== BOTONES =====
        single_mode_btn = ttk.Button(main_frame, text="📄  Modo Individual",
                                     style="Custom.TButton",
                                     command=lambda: launch_single_mode(mode_window))
        single_mode_btn.pack(pady=15, fill=tk.X, padx=60)

        massive_mode_btn = ttk.Button(main_frame, text="📂  Modo Masivo",
                                      style="Custom.TButton",
                                      command=lambda: launch_massive_mode(mode_window))
        massive_mode_btn.pack(pady=15, fill=tk.X, padx=60)

        # ===== FUNCIONES =====
        def launch_single_mode(window):
            window.destroy()
            app = PDFExtractorGUI()
            app.run()

        def launch_massive_mode(window):
            window.destroy()
            app = MassiveProcessorGUI()
            app.run()

        # ===== CENTRAR VENTANA =====
        mode_window.update_idletasks()
        x = (mode_window.winfo_screenwidth() // 2) - (mode_window.winfo_width() // 2)
        y = (mode_window.winfo_screenheight() // 2) - (mode_window.winfo_height() // 2)
        mode_window.geometry(f"+{x}+{y}")

        mode_window.mainloop()

    except Exception as e:
        logger.error(f"Error iniciando la aplicación: {e}")
        messagebox.showerror("Error Fatal", f"Error iniciando la aplicación: {e}")
