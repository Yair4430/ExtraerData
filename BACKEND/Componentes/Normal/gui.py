import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import List  # Importar List desde typing
import threading
import pandas as pd
from pathlib import Path
import os
from .constants import logger
from .data_models import DocumentoData
from .document_extractor import DocumentExtractor
from .file_processor import FileProcessor
from .excel_exporter import ExcelExporter  # Importar el nuevo componente

class PDFExtractorGUI:
    """Interfaz gráfica principal para el extractor de PDFs"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Extractor de Datos de Cédulas - v2.1 (Con Soporte Comprimidos)")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Variables
        self.ficha_var = tk.StringVar()
        self.folder_path = ""
        self.extracted_data: List[DocumentoData] = []  # Usar List en lugar de _List
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
        """Configura los estilos de la interfaz"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configurar colores personalizados
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'), foreground='#2c3e50')
        style.configure('Subtitle.TLabel', font=('Arial', 10, 'bold'), foreground='#34495e')
        style.configure('Success.TLabel', foreground='#27ae60')
        style.configure('Warning.TLabel', foreground='#e67e22')
        style.configure('Error.TLabel', foreground='#e74c3c')
        
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
        title_label = ttk.Label(main_frame, text="Extractor de Datos de Cédulas", style='Title.TLabel')
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Sección de configuración
        config_frame = ttk.LabelFrame(main_frame, text="Configuración", padding="10")
        config_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        config_frame.columnconfigure(1, weight=1)
        
        # Número de ficha
        ttk.Label(config_frame, text="Número de Ficha:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        ficha_entry = ttk.Entry(config_frame, textvariable=self.ficha_var, width=20)
        ficha_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        # Botón seleccionar carpeta
        self.folder_button = ttk.Button(config_frame, text="Seleccionar Carpeta", command=self.select_folder)
        self.folder_button.grid(row=0, column=2, padx=(0, 5))
        
        # Botón seleccionar archivo comprimido
        self.compressed_button = ttk.Button(config_frame, text="Archivo Comprimido", command=self.select_compressed_file)
        self.compressed_button.grid(row=0, column=3)
        
        # Label para mostrar carpeta o archivo seleccionado
        self.folder_label = ttk.Label(config_frame, text="Ninguna carpeta o archivo seleccionado", foreground='gray')
        self.folder_label.grid(row=1, column=0, columnspan=4, sticky=tk.W, pady=(5, 0))
        
        # Sección de procesamiento
        process_frame = ttk.LabelFrame(main_frame, text="Procesamiento", padding="10")
        process_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        process_frame.columnconfigure(0, weight=1)
        
        # Botones de acción
        button_frame = ttk.Frame(process_frame)
        button_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
        button_frame.columnconfigure(0, weight=1)
        
        self.process_button = ttk.Button(button_frame, text="Procesar PDFs", command=self.start_processing)
        self.process_button.grid(row=0, column=0, padx=(0, 5))
        
        self.preview_button = ttk.Button(button_frame, text="Vista Previa", command=self.show_preview, state='disabled')
        self.preview_button.grid(row=0, column=1, padx=5)
        
        self.export_button = ttk.Button(button_frame, text="Exportar Excel", command=self.export_to_excel, state='disabled')
        self.export_button.grid(row=0, column=2, padx=(5, 0))
        
        # Barra de progreso
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(process_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(10, 5))
        
        # Label de estado
        self.status_label = ttk.Label(process_frame, text="Listo para procesar")
        self.status_label.grid(row=2, column=0, sticky=tk.W)
        
        # Sección de resultados
        results_frame = ttk.LabelFrame(main_frame, text="Resultados", padding="10")
        results_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        results_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)
        
        # Treeview para mostrar resultados
        columns = ('Documento', 'Estado', 'Días Restantes', 'Archivo')
        self.tree = ttk.Treeview(results_frame, columns=columns, show='headings', height=10)
        
        # Configurar columnas
        self.tree.heading('Documento', text='Número de Documento')
        self.tree.heading('Estado', text='Estado')
        self.tree.heading('Días Restantes', text='Días Restantes')
        self.tree.heading('Archivo', text='Archivo Origen')
        
        self.tree.column('Documento', width=150)
        self.tree.column('Estado', width=100)
        self.tree.column('Días Restantes', width=120)
        self.tree.column('Archivo', width=200)
        
        # Scrollbar para el treeview
        scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        results_frame.rowconfigure(0, weight=1)
        
        # Frame de estadísticas
        stats_frame = ttk.Frame(main_frame)
        stats_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.stats_label = ttk.Label(stats_frame, text="")
        self.stats_label.grid(row=0, column=0, sticky=tk.W)
        
    def select_folder(self):
        """Selecciona la carpeta que contiene los PDFs"""
        # Abrir directamente en la carpeta de Descargas
        initial_dir = str(Path.home() / "Downloads")
        
        folder = filedialog.askdirectory(
            title="Seleccione la carpeta que contiene los PDFs",
            initialdir=initial_dir
        )
        if folder:
            self.folder_path = folder
            self.is_compressed_file = False
            self.folder_label.config(text=f"Carpeta: {folder}", foreground='black')
            logger.info(f"Carpeta seleccionada: {folder}")
            
    def select_compressed_file(self):
        """Selecciona un archivo comprimido que contiene los PDFs"""
        from .constants import RARFILE_AVAILABLE
        
        # Abrir directamente en la carpeta de Descargas
        initial_dir = str(Path.home() / "Downloads")
        
        # Definir tipos de archivo - SOLO ZIP
        filetypes = [
            ("Archivos ZIP", "*.zip"),  # Solo mostrar archivos ZIP
        ]
        
        file_path = filedialog.askopenfilename(
            title="Seleccione el archivo comprimido que contiene los PDFs",
            filetypes=filetypes,
            initialdir=initial_dir  # Abrir en Descargas
        )
        
        if file_path:
            self.folder_path = file_path
            self.is_compressed_file = True
            filename = os.path.basename(file_path)
            self.folder_label.config(text=f"Archivo comprimido: {filename}", foreground='black')
            logger.info(f"Archivo comprimido seleccionado: {file_path}")

    def start_processing(self):
        """Inicia el procesamiento de PDFs en un hilo separado"""
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
            self.root.after(0, lambda: self.status_label.config(text="Procesando PDFs..."))
            
            # Determinar la carpeta de trabajo
            work_folder = self.folder_path
            
            # Si es un archivo comprimido, extraerlo primero
            if self.is_compressed_file:
                self.root.after(0, lambda: self.status_label.config(text="Extrayendo archivo comprimido..."))
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
                    self.root.after(0, lambda f=pdf_filename: self.status_label.config(text=f"Procesando: {f}"))
                    
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
        self.folder_label.config(text="Ninguna carpeta o archivo seleccionado", foreground='gray')
        
        # Limpiar datos extraídos
        self.extracted_data = []
        
        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Resetear barra de progreso
        self.progress_var.set(0)
        
        # Limpiar estado y estadísticas
        self.status_label.config(text="Listo para procesar")
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
        self.tree.tag_configure('vigente', foreground='#27ae60')
        self.tree.tag_configure('por_vencer', foreground='#e67e22')
        self.tree.tag_configure('vencido', foreground='#e74c3c')
        
        # Actualizar estadísticas
        self.update_statistics()
        
        # Actualizar estado
        self.status_label.config(text=f"Procesamiento completado. {len(self.extracted_data)} documentos procesados.")
        
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
        
        stats_text = f"Total: {total} | Vigentes: {vigentes} | Por vencer: {por_vencer} | Vencidos: {vencidos}"
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
        
        # Frame principal
        main_frame = ttk.Frame(preview_window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Treeview con más detalles
        columns = ('Tipo', 'Documento', 'Nombres', 'Fecha Exp.', 'Estado', 'Días Rest.', 'Archivo')
        tree = ttk.Treeview(main_frame, columns=columns, show='headings')
        
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
                
                messagebox.showinfo("Éxito", f"Datos exportados exitosamente a:\n{file_path}")
                self.reset_form()

            except Exception as e:
                logger.error(f"Error exportando a Excel: {e}")
                messagebox.showerror("Error", f"Error exportando a Excel: {e}")
                
    def update_ui_state(self, enabled: bool):
        """Actualiza el estado de los elementos de la UI"""
        state = 'normal' if enabled else 'disabled'
        self.process_button.config(state=state)
        self.folder_button.config(state=state)
        self.compressed_button.config(state=state)
        
        if enabled and self.extracted_data:
            self.preview_button.config(state='normal')
            self.export_button.config(state='normal')
        else:
            self.preview_button.config(state='disabled')
            self.export_button.config(state='disabled')
        
    def run(self):
        """Ejecuta la aplicación"""
        self.root.mainloop()