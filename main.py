"""
Extractor de Datos de PDFs de Cédulas - Versión Mejorada con Soporte para Archivos Comprimidos
Extrae información de cédulas de ciudadanía desde archivos PDF y genera reportes en Excel
"""

import os
import re
import logging
import pdfplumber
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import json
from dataclasses import dataclass, asdict
import zipfile
import tempfile
import shutil

# Try to import rarfile (optional dependency)
try:
    import rarfile
    RARFILE_AVAILABLE = True
except ImportError:
    RARFILE_AVAILABLE = False
    logging.warning("rarfile no está disponible. Solo se soportarán archivos ZIP.")

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pdf_extractor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Constantes
MESES = {
    'Enero': 1, 'Febrero': 2, 'Marzo': 3, 'Abril': 4, 'Mayo': 5, 'Junio': 6,
    'Julio': 7, 'Agosto': 8, 'Septiembre': 9, 'Octubre': 10, 'Noviembre': 11, 'Diciembre': 12
}

DIAS_ALERTA_VENCIMIENTO = 30  # Días antes del vencimiento para alertar

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
    dias_restantes: int
    estado: str
    archivo_origen: str

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
        self.extracted_data: List[DocumentoData] = []
        self.processing = False
        self.is_compressed_file = False
        self.temp_dir = None
        
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
        folder = filedialog.askdirectory(title="Seleccione la carpeta que contiene los PDFs")
        if folder:
            self.folder_path = folder
            self.is_compressed_file = False
            self.folder_label.config(text=f"Carpeta: {folder}", foreground='black')
            logger.info(f"Carpeta seleccionada: {folder}")
            
    def select_compressed_file(self):
        """Selecciona un archivo comprimido que contiene los PDFs"""
        filetypes = [
            ("Archivos comprimidos", "*.zip"),
            ("Archivos ZIP", "*.zip"),
        ]
        
        if RARFILE_AVAILABLE:
            filetypes.insert(1, ("Archivos RAR", "*.rar"))
            filetypes[0] = ("Archivos comprimidos", "*.zip;*.rar")
        
        file_path = filedialog.askopenfilename(
            title="Seleccione el archivo comprimido que contiene los PDFs",
            filetypes=filetypes
        )
        
        if file_path:
            self.folder_path = file_path
            self.is_compressed_file = True
            filename = os.path.basename(file_path)
            self.folder_label.config(text=f"Archivo comprimido: {filename}", foreground='black')
            logger.info(f"Archivo comprimido seleccionado: {file_path}")

    def extract_compressed_file(self, file_path: str) -> str:
        """Extrae un archivo comprimido a una carpeta temporal"""
        try:
            # Crear directorio temporal
            self.temp_dir = tempfile.mkdtemp(prefix="pdf_extractor_")
            
            file_extension = os.path.splitext(file_path)[1].lower()
            
            if file_extension == '.zip':
                with zipfile.ZipFile(file_path, 'r') as zip_ref:
                    # Extraer solo archivos PDF
                    pdf_files = [f for f in zip_ref.namelist() if f.lower().endswith('.pdf')]
                    for pdf_file in pdf_files:
                        zip_ref.extract(pdf_file, self.temp_dir)
                    logger.info(f"Extraídos {len(pdf_files)} archivos PDF del ZIP")
                    
            elif file_extension == '.rar' and RARFILE_AVAILABLE:
                with rarfile.RarFile(file_path, 'r') as rar_ref:
                    # Extraer solo archivos PDF
                    pdf_files = [f for f in rar_ref.namelist() if f.lower().endswith('.pdf')]
                    for pdf_file in pdf_files:
                        rar_ref.extract(pdf_file, self.temp_dir)
                    logger.info(f"Extraídos {len(pdf_files)} archivos PDF del RAR")
                    
            else:
                raise ValueError(f"Formato de archivo no soportado: {file_extension}")
                
            return self.temp_dir
            
        except Exception as e:
            logger.error(f"Error extrayendo archivo comprimido: {e}")
            if self.temp_dir and os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
                self.temp_dir = None
            raise

    def cleanup_temp_files(self):
        """Limpia los archivos temporales"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir)
                self.temp_dir = None
                logger.info("Archivos temporales limpiados")
            except Exception as e:
                logger.error(f"Error limpiando archivos temporales: {e}")
            
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
                work_folder = self.extract_compressed_file(self.folder_path)
            
            # Buscar archivos PDF recursivamente si es necesario
            pdf_files = []
            for root, dirs, files in os.walk(work_folder):
                for file in files:
                    if file.lower().endswith('.pdf'):
                        pdf_files.append(os.path.join(root, file))
            
            total_files = len(pdf_files)
            
            if total_files == 0:
                self.root.after(0, lambda: messagebox.showwarning("Aviso", "No se encontraron archivos PDF en la ubicación seleccionada."))
                return
                
            self.extracted_data = []
            
            for idx, pdf_path in enumerate(pdf_files, 1):
                pdf_filename = os.path.basename(pdf_path)
                
                try:
                    self.root.after(0, lambda f=pdf_filename: self.status_label.config(text=f"Procesando: {f}"))
                    
                    text = self.extract_text_from_pdf(pdf_path)
                    document_data = self.extract_document_data(text, pdf_filename)
                    
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
                self.cleanup_temp_files()
            self.processing = False
            self.root.after(0, lambda: self.update_ui_state(True))
            
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extrae texto de un archivo PDF"""
        text = ''
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + '\n'
        return text
        

    def reset_form(self):
        """Limpia todos los campos para un nuevo proceso"""
        if self.is_compressed_file:
            self.cleanup_temp_files()
            
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

        
    def extract_document_data(self, text: str, filename: str) -> Optional[DocumentoData]:
        """Extrae los datos del documento desde el texto"""
        try:
            # Patrones de búsqueda mejorados
            cedula_match = re.search(r'C[eé]dula de Ciudadan[ií]a:\s*([\d\.]+)', text)
            fecha_match = re.search(r'Fecha de Expedici[oó]n:\s*(\d{1,2})\s+DE\s+([A-Z]+)\s+DE\s+(\d{4})', text, re.IGNORECASE)
            vigencia_match = re.search(r'válida en todo el territorio nacional hasta el (\d{1,2}) de ([A-Za-z]+) de (\d{4})', text, re.IGNORECASE)
            
            # Intentar extraer nombres (patrón común en cédulas)
            nombres_match = re.search(r'Nombres:\s*([A-ZÁÉÍÓÚÑ\s]+)', text) or re.search(r'NOMBRES:\s*([A-ZÁÉÍÓÚÑ\s]+)', text)
            apellidos_match = re.search(r'Apellidos:\s*([A-ZÁÉÍÓÚÑ\s]+)', text) or re.search(r'APELLIDOS:\s*([A-ZÁÉÍÓÚÑ\s]+)', text)
            
            if not cedula_match or not fecha_match or not vigencia_match:
                return None
                
            cedula = cedula_match.group(1).replace('.', '')
            dia, mes, anio = fecha_match.group(1), fecha_match.group(2).capitalize(), fecha_match.group(3)
            
            # Construir nombre completo
            nombres_apellidos = "N/A"
            if nombres_match and apellidos_match:
                nombres = nombres_match.group(1).strip()
                apellidos = apellidos_match.group(1).strip()
                nombres_apellidos = f"{nombres} {apellidos}"
            elif nombres_match:
                nombres_apellidos = nombres_match.group(1).strip()
                
            # Fecha de vigencia
            dia_v, mes_v, anio_v = vigencia_match.group(1), vigencia_match.group(2).capitalize(), vigencia_match.group(3)
            fecha_vigencia = datetime(int(anio_v), MESES.get(mes_v, 1), int(dia_v))
            
            # Calcular días restantes y estado
            dias_restantes = (fecha_vigencia - datetime.now()).days
            
            if dias_restantes < 0:
                estado = 'VENCIDO'
            elif dias_restantes <= DIAS_ALERTA_VENCIMIENTO:
                estado = 'POR VENCER'
            else:
                estado = 'VIGENTE'
                
            return DocumentoData(
                tipo_documento='CC',
                numero_documento=cedula,
                nombres_apellidos=nombres_apellidos,
                dia=dia,
                mes=mes,
                año=anio,
                fecha_vigencia=fecha_vigencia,
                dias_restantes=dias_restantes,
                estado=estado,
                archivo_origen=filename
            )
            
        except Exception as e:
            logger.error(f"Error extrayendo datos del documento: {e}")
            return None
            
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
            tree.insert('', 'end', values=(data.tipo_documento, data.numero_documento, data.nombres_apellidos, fecha_exp, data.estado, data.dias_restantes, data.archivo_origen))
            
        # Posicionar elementos
        tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)
        
    def export_to_excel(self):
        """Exporta los datos a un archivo Excel (sin campos de vigencia ni archivo de origen)"""
        if not self.extracted_data:
            messagebox.showwarning("Aviso", "No hay datos para exportar.")
            return

        try:
            # Preparar datos para DataFrame (solo los campos necesarios)
            data_for_df = []
            for data in self.extracted_data:
                data_dict = {
                    'TIPO DE DOCUMENTO': data.tipo_documento,
                    'NUMERO DE DOCUMENTO': data.numero_documento,
                    'NOMBRES Y APELLIDOS': data.nombres_apellidos,
                    'DIA': data.dia,
                    'MES': data.mes,
                    'AÑO': data.año,
                }
                data_for_df.append(data_dict)

            # Crear DataFrame
            df = pd.DataFrame(data_for_df)

            # Guardar automáticamente en Descargas
            ficha = self.ficha_var.get().strip()
            filename = f'plantilla_{ficha}.xlsx'
            downloads_path = str(Path.home() / "Downloads")
            file_path = os.path.join(downloads_path, filename)

            # Guardar Excel
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Datos', index=False)

            logger.info(f"Datos exportados exitosamente a: {file_path}")
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
