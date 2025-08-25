import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import List
import threading
import pandas as pd
from pathlib import Path
import os
from .constants import logger
from .data_models import DocumentoData
from .document_extractor import DocumentExtractor
from .file_processor import FileProcessor
from .excel_exporter import ExcelExporter

class PDFExtractorGUI:
    """Interfaz gráfica principal para el extractor de PDFs con diseño mejorado"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Extractor de Datos de Cédulas - v2.1 (Con Soporte Comprimidos)")
        self.root.geometry("850x650")
        self.root.resizable(True, True)
        
        # Variables
        self.ficha_var = tk.StringVar()
        self.folder_path = ""
        self.extracted_data: List[DocumentoData] = []
        self.processing = False
        self.is_compressed_file = False
        
        # Componentes
        self.extractor = DocumentExtractor()
        self.file_processor = FileProcessor()
        self.excel_exporter = ExcelExporter()

        # Configurar estilo
        self.setup_styles()
        self.create_widgets()
        self.center_window()
        
    def setup_styles(self):
        """Configura los estilos de la interfaz con un diseño más moderno"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Paleta de colores moderna
        self.bg_color = "#1E1E2E"  # Fondo oscuro
        self.card_color = "#2A2A3A"  # Color de tarjeta
        self.accent_color = "#5B6EE1"  # Azul moderno
        self.accent_hover = "#4A5AD0"  # Azul hover
        self.success_color = "#38A169"  # Verde para éxito
        self.warning_color = "#D69E2E"  # Amarillo para advertencia
        self.error_color = "#E53E3E"  # Rojo para error
        self.text_color = "#FFFFFF"  # Texto blanco
        self.subtitle_color = "#A0AEC0"  # Texto secundario
        
        self.root.configure(bg=self.bg_color)
        
        # Configurar estilos
        style.configure('Title.TLabel', 
                       font=('Segoe UI', 18, 'bold'), 
                       foreground=self.text_color,
                       background=self.bg_color)
        
        style.configure('Subtitle.TLabel', 
                       font=('Segoe UI', 11), 
                       foreground=self.subtitle_color,
                       background=self.bg_color)
        
        style.configure('Card.TFrame',
                       background=self.card_color)
        
        style.configure('CardHeader.TLabel',
                       font=('Segoe UI', 12, 'bold'),
                       foreground=self.text_color,
                       background=self.card_color)
        
        style.configure('Primary.TButton',
                       font=('Segoe UI', 10, 'bold'),
                       padding=10,
                       relief='flat',
                       background=self.accent_color,
                       foreground=self.text_color,
                       focuscolor=self.card_color)
        style.map('Primary.TButton',
                 background=[('active', self.accent_hover)],
                 foreground=[('active', self.text_color)])
        
        style.configure('Secondary.TButton',
                       font=('Segoe UI', 10),
                       padding=8,
                       relief='flat',
                       background="#374151",
                       foreground=self.text_color,
                       focuscolor=self.card_color)
        style.map('Secondary.TButton',
                 background=[('active', '#4B5563')],
                 foreground=[('active', self.text_color)])
        
        style.configure('Custom.Horizontal.TProgressbar',
                       troughcolor=self.card_color,
                       bordercolor=self.card_color,
                       background=self.accent_color,
                       lightcolor=self.accent_color,
                       darkcolor=self.accent_color)
        
        # Configurar colores para el treeview
        style.configure('Treeview',
                       background=self.card_color,
                       foreground=self.text_color,
                       fieldbackground=self.card_color,
                       borderwidth=0)
        style.configure('Treeview.Heading',
                       background=self.accent_color,
                       foreground=self.text_color,
                       relief='flat',
                       font=('Segoe UI', 10, 'bold'))
        style.map('Treeview.Heading',
                 background=[('active', self.accent_hover)])
        
    def center_window(self):
        """Centra la ventana en la pantalla"""
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (self.root.winfo_width() // 2)
        y = (self.root.winfo_screenheight() // 2) - (self.root.winfo_height() // 2)
        self.root.geometry(f"+{x}+{y}")
        
    def create_widgets(self):
        """Crea todos los widgets de la interfaz con diseño mejorado"""
        # Frame principal
        main_frame = tk.Frame(self.root, bg=self.bg_color, padx=25, pady=25)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title_label = ttk.Label(main_frame, text="Extractor de Datos de Cédulas", style='Title.TLabel')
        title_label.pack(pady=(0, 10))
        
        subtitle_label = ttk.Label(main_frame, 
                                  text="v2.1 (Con Soporte Comprimidos)", 
                                  style='Subtitle.TLabel')
        subtitle_label.pack(pady=(0, 20))
        
        # Botón volver al menú principal (colocado arriba)
        self.back_button = ttk.Button(main_frame, text="🏠 Volver al Menú Principal",
                                     style='Secondary.TButton', command=self.back_to_menu)
        self.back_button.pack(pady=(0, 20), fill=tk.X)
        
        # Tarjeta de configuración
        config_card = tk.Frame(main_frame, bg=self.card_color, padx=15, pady=15, relief='flat')
        config_card.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(config_card, text="⚙️ Configuración", 
                 font=('Segoe UI', 12, 'bold'), 
                 foreground=self.text_color, 
                 background=self.card_color).pack(anchor='w', pady=(0, 10))
        
        # Frame para inputs
        input_frame = tk.Frame(config_card, bg=self.card_color)
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Número de ficha
        ttk.Label(input_frame, text="Número de Ficha:", 
                 foreground=self.text_color, 
                 background=self.card_color).grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        
        ficha_entry = ttk.Entry(input_frame, textvariable=self.ficha_var, width=20, font=('Segoe UI', 10))
        ficha_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        # Botones de selección
        btn_frame = tk.Frame(input_frame, bg=self.card_color)
        btn_frame.grid(row=0, column=2, columnspan=2, sticky=tk.E)
        
        self.folder_button = ttk.Button(btn_frame, text="📂 Seleccionar Carpeta", 
                                       style='Secondary.TButton', command=self.select_folder)
        self.folder_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.compressed_button = ttk.Button(btn_frame, text="📦 Archivo Comprimido", 
                                           style='Secondary.TButton', command=self.select_compressed_file)
        self.compressed_button.pack(side=tk.LEFT)
        
        input_frame.columnconfigure(1, weight=1)
        
        # Label para mostrar carpeta o archivo seleccionado
        self.folder_label = ttk.Label(config_card, text="Ninguna carpeta o archivo seleccionado", 
                                     foreground=self.subtitle_color, 
                                     background=self.card_color,
                                     wraplength=700)
        self.folder_label.pack(anchor='w', pady=(5, 0))
        
        # Tarjeta de procesamiento
        process_card = tk.Frame(main_frame, bg=self.card_color, padx=15, pady=15, relief='flat')
        process_card.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(process_card, text="🔄 Procesamiento", 
                 font=('Segoe UI', 12, 'bold'), 
                 foreground=self.text_color, 
                 background=self.card_color).pack(anchor='w', pady=(0, 10))
        
        # Botones de acción
        button_frame = tk.Frame(process_card, bg=self.card_color)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.process_button = ttk.Button(button_frame, text="⚡ Procesar PDFs", 
                                        style='Primary.TButton', command=self.start_processing)
        self.process_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.preview_button = ttk.Button(button_frame, text="👁️ Vista Previa", 
                                        style='Secondary.TButton', command=self.show_preview, state='disabled')
        self.preview_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.export_button = ttk.Button(button_frame, text="💾 Exportar Excel", 
                                       style='Secondary.TButton', command=self.export_to_excel, state='disabled')
        self.export_button.pack(side=tk.LEFT)
        
        # Barra de progreso
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(process_card, variable=self.progress_var, 
                                           maximum=100, style='Custom.Horizontal.TProgressbar')
        self.progress_bar.pack(fill=tk.X, pady=(10, 5))
        
        # Label de estado
        self.status_label = ttk.Label(process_card, text="✅ Listo para procesar", 
                                     foreground=self.subtitle_color, 
                                     background=self.card_color)
        self.status_label.pack(anchor='w')
        
        # Tarjeta de resultados
        results_card = tk.Frame(main_frame, bg=self.card_color, padx=15, pady=15, relief='flat')
        results_card.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        ttk.Label(results_card, text="📊 Resultados", 
                 font=('Segoe UI', 12, 'bold'), 
                 foreground=self.text_color, 
                 background=self.card_color).pack(anchor='w', pady=(0, 10))
        
        # Frame para treeview y scrollbar
        tree_frame = tk.Frame(results_card, bg=self.card_color)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Treeview para mostrar resultados
        columns = ('Documento', 'Estado', 'Días Restantes', 'Archivo')
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=12)
        
        # Configurar columnas
        column_widths = {'Documento': 150, 'Estado': 100, 'Días Restantes': 120, 'Archivo': 250}
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=column_widths[col])
        
        # Scrollbar para el treeview
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Frame de estadísticas
        stats_frame = tk.Frame(results_card, bg=self.card_color)
        stats_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.stats_label = ttk.Label(stats_frame, text="", 
                                    foreground=self.subtitle_color, 
                                    background=self.card_color)
        self.stats_label.pack(anchor='w')
        
    def back_to_menu(self):
        """Volver al menú principal"""
        if self.processing:
            if not messagebox.askyesno("Confirmar", "El procesamiento está en curso. ¿Está seguro de que desea salir?"):
                return
                
        self.root.destroy()
        # Importar aquí para evitar dependencia circular
        try:
            from contenedor import contenedor  
            contenedor()
        except ImportError:
            logger.warning("No se pudo importar el módulo contenedor")
            
    def select_folder(self):
        """Selecciona la carpeta que contiene los PDFs"""
        if self.processing:
            return
            
        initial_dir = str(Path.home() / "Downloads")
        
        folder = filedialog.askdirectory(
            title="Seleccione la carpeta que contiene los PDFs",
            initialdir=initial_dir
        )
        if folder:
            self.folder_path = folder
            self.is_compressed_file = False
            display_text = folder if len(folder) < 60 else f"...{folder[-57:]}"
            self.folder_label.config(text=f"📁 Carpeta: {display_text}", foreground=self.text_color)
            logger.info(f"Carpeta seleccionada: {folder}")
            
    def select_compressed_file(self):
        """Selecciona un archivo comprimido que contiene los PDFs"""
        if self.processing:
            return
            
        from .constants import RARFILE_AVAILABLE
        
        initial_dir = str(Path.home() / "Downloads")
        
        # Definir tipos de archivo - SOLO ZIP
        filetypes = [
            ("Archivos ZIP", "*.zip"),
        ]
        
        file_path = filedialog.askopenfilename(
            title="Seleccione el archivo comprimido que contiene los PDFs",
            filetypes=filetypes,
            initialdir=initial_dir
        )
        
        if file_path:
            self.folder_path = file_path
            self.is_compressed_file = True
            filename = os.path.basename(file_path)
            display_text = filename if len(filename) < 60 else f"...{filename[-57:]}"
            self.folder_label.config(text=f"📦 Archivo comprimido: {display_text}", foreground=self.text_color)
            logger.info(f"Archivo comprimido seleccionado: {file_path}")

    def start_processing(self):
        """Inicia el procesamiento de PDFs en un hilo separado"""
        if self.processing:
            return
            
        if not self.validate_inputs():
            return
            
        self.processing = True
        self.update_ui_state(False)
        
        # Ejecutar en hilo separado para no bloquear la UI
        thread = threading.Thread(target=self.process_pdfs)
        thread.daemon = True
        thread.start()
        
    def validate_inputs(self) -> bool:
        """Valida las entradas del usuario"""
        if not self.ficha_var.get().strip():
            messagebox.showerror("Error", "Debe ingresar un número de ficha válido.")
            return False
            
        if not self.folder_path:
            messagebox.showerror("Error", "Debe seleccionar una carpeta o archivo comprimido.")
            return False
            
        if self.is_compressed_file:
            if not os.path.exists(self.folder_path):
                messagebox.showerror("Error", "El archivo comprimido seleccionado no existe.")
                return False
        else:
            if not os.path.isdir(self.folder_path):
                messagebox.showerror("Error", "La carpeta seleccionada no existe.")
                return False
            
        return True
        
    def process_pdfs(self):
        """Procesa todos los PDFs en la carpeta seleccionada o archivo comprimido"""
        try:
            self.root.after(0, lambda: self.status_label.config(text="🔄 Procesando PDFs..."))
            
            # Determinar la carpeta de trabajo
            work_folder = self.folder_path
            
            # Si es un archivo comprimido, extraerlo primero
            if self.is_compressed_file:
                self.root.after(0, lambda: self.status_label.config(text="📦 Extrayendo archivo comprimido..."))
                work_folder = self.file_processor.extract_compressed_file(self.folder_path)
            
            # Buscar archivos PDF
            pdf_files = self.file_processor.find_pdf_files(work_folder)
            
            total_files = len(pdf_files)
            
            if total_files == 0:
                self.root.after(0, lambda: messagebox.showwarning("Aviso", "No se encontraron archivos PDF en la ubicación seleccionada."))
                return
                
            self.extracted_data = []
            
            for idx, pdf_path in enumerate(pdf_files, 1):
                pdf_filename = os.path.basename(pdf_path)
                
                try:
                    self.root.after(0, lambda f=pdf_filename: self.status_label.config(text=f"📄 Procesando: {f}"))
                    
                    text = self.extractor.extract_text_from_pdf(pdf_path)
                    document_data = self.extractor.extract_document_data(text, pdf_filename)
                    
                    if document_data:
                        self.extracted_data.append(document_data)
                        logger.info(f"Procesado exitosamente: {pdf_filename}")
                    else:
                        logger.warning(f"No se encontraron datos válidos en: {pdf_filename}")
                        
                except Exception as e:
                    logger.error(f"Error procesando {pdf_filename}: {e}")
                    
                # Actualizar barra de progreso
                progress = (idx / total_files) * 100
                self.root.after(0, lambda p=progress: self.progress_var.set(p))
                
            # Actualizar UI con resultados
            self.root.after(0, self.update_results)
            
        except Exception as e:
            logger.error(f"Error durante el procesamiento: {e}")
            self.root.after(0, lambda: messagebox.showerror("Error", f"Error durante el procesamiento: {e}"))
        finally:
            if self.is_compressed_file:
                self.file_processor.cleanup_temp_files()
            self.processing = False
            self.root.after(0, lambda: self.update_ui_state(True))
            
    def reset_form(self):
        """Limpia todos los campos para un nuevo proceso"""
        if self.is_compressed_file:
            self.file_processor.cleanup_temp_files()
            
        # Limpiar entrada
        self.ficha_var.set("")
        
        # Limpiar carpeta seleccionada
        self.folder_path = ""
        self.is_compressed_file = False
        self.folder_label.config(text="Ninguna carpeta o archivo seleccionado", foreground=self.subtitle_color)
        
        # Limpiar datos extraídos
        self.extracted_data = []
        
        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Resetear barra de progreso
        self.progress_var.set(0)
        
        # Limpiar estado y estadísticas
        self.status_label.config(text="✅ Listo para procesar")
        self.stats_label.config(text="")
        
        # Desactivar botones de vista previa y exportación
        self.preview_button.config(state='disabled')
        self.export_button.config(state='disabled')

    def update_results(self):
        """Actualiza la vista de resultados"""
        # Limpiar treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Agregar datos
        for data in self.extracted_data:
            # Configurar color según estado
            tags = []
            if data.estado == 'VIGENTE':
                tags = ['vigente']
            elif data.estado == 'POR VENCER':
                tags = ['por_vencer']
            else:
                tags = ['vencido']
                
            self.tree.insert('', 'end', values=(data.numero_documento, data.estado, data.dias_restantes, data.archivo_origen), tags=tags)
            
        # Configurar colores de las filas
        self.tree.tag_configure('vigente', foreground=self.success_color)
        self.tree.tag_configure('por_vencer', foreground=self.warning_color)
        self.tree.tag_configure('vencido', foreground=self.error_color)
        
        # Actualizar estadísticas
        self.update_statistics()
        
        # Actualizar estado
        self.status_label.config(text=f"✅ Procesamiento completado. {len(self.extracted_data)} documentos procesados.")
        
        # Reproducir sonido de finalización
        try:
            import winsound
            winsound.Beep(1000, 300)
        except ImportError:
            pass  # No disponible en sistemas no Windows
            
    def update_statistics(self):
        """Actualiza las estadísticas mostradas"""
        if not self.extracted_data:
            self.stats_label.config(text="")
            return
            
        total = len(self.extracted_data)
        vigentes = sum(1 for d in self.extracted_data if d.estado == 'VIGENTE')
        por_vencer = sum(1 for d in self.extracted_data if d.estado == 'POR VENCER')
        vencidos = sum(1 for d in self.extracted_data if d.estado == 'VENCIDO')
        
        stats_text = f"📈 Total: {total} | ✅ Vigentes: {vigentes} | ⚠️ Por vencer: {por_vencer} | ❌ Vencidos: {vencidos}"
        self.stats_label.config(text=stats_text)
        
    def show_preview(self):
        """Muestra una ventana de vista previa de los datos"""
        from .constants import MESES
        
        if not self.extracted_data:
            messagebox.showwarning("Aviso", "No hay datos para mostrar.")
            return
            
        preview_window = tk.Toplevel(self.root)
        preview_window.title("Vista Previa de Datos")
        preview_window.geometry("900x500")
        preview_window.configure(bg=self.bg_color)
        
        # Frame principal
        main_frame = tk.Frame(preview_window, bg=self.bg_color, padx=15, pady=15)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Treeview con más detalles
        columns = ('Tipo', 'Documento', 'Nombres', 'Fecha Exp.', 'Estado', 'Días Rest.', 'Archivo')
        tree = ttk.Treeview(main_frame, columns=columns, show='headings', style='Treeview')
        
        # Configurar columnas
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120)
            
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=tree.yview)
        h_scrollbar = ttk.Scrollbar(main_frame, orient=tk.HORIZONTAL, command=tree.xview)
        tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Agregar datos
        for data in self.extracted_data:
            fecha_exp = f"{data.dia}/{MESES.get(data.mes, 1)}/{data.año}"
            
            # Mostrar "N/A" para días restantes en documentos TI
            if data.tipo_documento == 'TI':
                dias_restantes_str = "N/A"
            else:
                dias_restantes_str = str(data.dias_restantes)
            
            tree.insert('', 'end', values=(
                data.tipo_documento, 
                data.numero_documento, 
                data.nombres_apellidos, 
                fecha_exp, 
                data.estado, 
                dias_restantes_str,
                data.archivo_origen
            ))
            
        # Posicionar elementos
        tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)
            
    def export_to_excel(self):
        """Exporta los datos a un archivo Excel usando el componente ExcelExporter"""
        if not self.extracted_data:
            messagebox.showwarning("Aviso", "No hay datos para exportar.")
            return

        try:
            ficha = self.ficha_var.get().strip()
            if not ficha:
                messagebox.showerror("Error", "Debe ingresar un número de ficha para exportar.")
                return
                
            file_path = self.excel_exporter.export_to_excel(self.extracted_data, ficha)
            
            messagebox.showinfo("Éxito", f"✅ Datos exportados exitosamente a:\n{file_path}")
            self.reset_form()

        except Exception as e:
            logger.error(f"Error exportando a Excel: {e}")
            messagebox.showerror("Error", f"❌ Error exportando a Excel: {e}")
                
    def update_ui_state(self, enabled: bool):
        """Actualiza el estado de los elementos de la UI"""
        state = 'normal' if enabled else 'disabled'
        self.process_button.config(state=state)
        self.folder_button.config(state=state)
        self.compressed_button.config(state=state)
        self.back_button.config(state=state)
        
        if enabled and self.extracted_data:
            self.preview_button.config(state='normal')
            self.export_button.config(state='normal')
        else:
            self.preview_button.config(state='disabled')
            self.export_button.config(state='disabled')
        
    def run(self):
        """Ejecuta la aplicación"""
        self.root.mainloop()