import { FaInfoCircle, FaTimes, FaFolder, FaDatabase, FaRobot, FaFilePdf, FaFileExcel, FaSearch, FaDownload, FaCogs } from "react-icons/fa"
import "./infoModalMasivo.css"

export default function InfoModalMasivo({ isOpen, onClose }) {
  if (!isOpen) return null

  return (
    <div className="masivo-modalOverlay" onClick={onClose}>
      <div className="masivo-modalContent" onClick={(e) => e.stopPropagation()}>
        
        {/* CABECERA DEL MODAL */}
        <div className="masivo-modalHeader">
          <h2 className="masivo-modalTitle">
            <FaInfoCircle className="masivo-modalIcon" />
            ¿Cómo funciona el Procesamiento Masivo?
          </h2>
          <button className="masivo-closeButton" onClick={onClose}>
            <FaTimes />
          </button>
        </div>

        {/* CUERPO PRINCIPAL */}
        <div className="masivo-modalBody">
          
          {/* DESCRIPCIÓN GENERAL */}
          <div className="masivo-infoSection">
            <h3 className="masivo-sectionHeader">
              <FaCogs className="masivo-stepIcon" />
              Sistema de Procesamiento Masivo
            </h3>
            <p className="masivo-infoText">
              El módulo masivo de <strong>ExtraerData</strong> procesa automáticamente múltiples carpetas 
              y archivos ZIP que contengan documentos PDF de identificación. El sistema recorre recursivamente 
              toda la estructura de carpetas, extrae datos de los PDFs y genera archivos Excel individuales 
              que luego son comprimidos en un único archivo ZIP.
            </p>
          </div>

          {/* ESTRUCTURA DE CARPETAS SOPORTADA */}
          <div className="masivo-infoSection">
            <h3 className="masivo-sectionHeader">
              <FaFolder className="masivo-stepIcon" />
              Estructura Soportada
            </h3>
            <div className="masivo-structureTypes">
              <div className="masivo-structureItem">
                <strong>📁 Subcarpetas:</strong> Todas las carpetas dentro del directorio principal
              </div>
              <div className="masivo-structureItem">
                <strong>📦 Archivos ZIP:</strong> Archivos comprimidos en el directorio principal
              </div>
              <div className="masivo-structureItem">
                <strong>🔍 Búsqueda Recursiva:</strong> Encuentra PDFs en todas las subcarpetas
              </div>
            </div>
          </div>

          {/* PROCESO DE EXTRACCIÓN MASIVA */}
          <div className="masivo-infoSection">
            <h3 className="masivo-sectionHeader">
              <FaRobot className="masivo-stepIcon" />
              Proceso de Extracción Masiva
            </h3>
            <div className="masivo-processSteps">
              <div className="masivo-step">
                <span className="masivo-stepNumber">1</span>
                <div className="masivo-stepContent">
                  <strong>Exploración Inicial:</strong> Escanea el directorio principal buscando subcarpetas y archivos ZIP
                </div>
              </div>
              <div className="masivo-step">
                <span className="masivo-stepNumber">2</span>
                <div className="masivo-stepContent">
                  <strong>Procesamiento Individual:</strong> Cada carpeta/ZIP se procesa de forma independiente
                </div>
              </div>
              <div className="masivo-step">
                <span className="masivo-stepNumber">3</span>
                <div className="masivo-stepContent">
                  <strong>Extracción de PDFs:</strong> Busca recursivamente todos los archivos PDF en cada elemento
                </div>
              </div>
              <div className="masivo-step">
                <span className="masivo-stepNumber">4</span>
                <div className="masivo-stepContent">
                  <strong>Análisis de Documentos:</strong> Aplica OCR y patrones para extraer datos estructurados
                </div>
              </div>
              <div className="masivo-step">
                <span className="masivo-stepNumber">5</span>
                <div className="masivo-stepContent">
                  <strong>Generación de Excel:</strong> Crea un archivo Excel por cada carpeta/ZIP procesado
                </div>
              </div>
              <div className="masivo-step">
                <span className="masivo-stepNumber">6</span>
                <div className="masivo-stepContent">
                  <strong>Compresión Final:</strong> Todos los Excel se comprimen en un archivo ZIP único
                </div>
              </div>
            </div>
          </div>

          {/* TIPOS DE DOCUMENTO SOPORTADOS */}
          <div className="masivo-infoSection">
            <h3 className="masivo-sectionHeader">
              <FaFilePdf className="masivo-stepIcon" />
              Documentos Soportados
            </h3>
            <div className="masivo-documentTypes">
              <div className="masivo-docType"><strong>CC:</strong> Cédula de Ciudadanía Colombiana</div>
              <div className="masivo-docType"><strong>TI:</strong> Tarjeta de Identidad</div>
              <div className="masivo-docType"><strong>PPT:</strong> Permiso Por Protección Temporal</div>
              <div className="masivo-docType"><strong>CE:</strong> Cédula de Extranjería</div>
            </div>
          </div>

          {/* DATOS EXTRAÍDOS */}
          <div className="masivo-infoSection">
            <h3 className="masivo-sectionHeader">
              <FaDatabase className="masivo-stepIcon" />
              Información Extraída
            </h3>
            <div className="masivo-dataExtracted">
              <div className="masivo-dataItem">• Tipo de documento identificado automáticamente</div>
              <div className="masivo-dataItem">• Número completo del documento</div>
              <div className="masivo-dataItem">• Nombres y apellidos del titular</div>
              <div className="masivo-dataItem">• Fecha de expedición (día, mes, año)</div>
            </div>
          </div>

          {/* RESULTADOS Y EXPORTACIÓN */}
          <div className="masivo-infoSection">
            <h3 className="masivo-sectionHeader">
              <FaFileExcel className="masivo-stepIcon" />
              Resultados y Exportación
            </h3>
            <div className="masivo-resultSection">
              <div className="masivo-resultItem">
                <FaDownload className="masivo-resultIcon" />
                <div>
                  <strong>Archivo ZIP Consolidado:</strong> Todos los Excel generados se comprimen en un único archivo 
                  llamado <code>excel_con_resultados.zip</code> que se guarda en la carpeta principal seleccionada.
                </div>
              </div>
              <div className="masivo-resultItem">
                <FaDatabase className="masivo-resultIcon" />
                <div>
                  <strong>Excel Individuales:</strong> Cada carpeta/ZIP procesado genera su propio archivo Excel 
                  con nombre <code>plantilla_[nombre_carpeta].xlsx</code>
                </div>
              </div>
              <div className="masivo-resultItem">
                <FaSearch className="masivo-resultIcon" />
                <div>
                  <strong>Validaciones Integradas:</strong> Los Excel incluyen listas desplegables y validaciones 
                  para asegurar la calidad y consistencia de los datos extraídos.
                </div>
              </div>
            </div>
          </div>

          {/* INSTRUCCIONES DE USO */}
          <div className="masivo-infoSection">
            <h3 className="masivo-sectionHeader">
              <FaRobot className="masivo-stepIcon" />
              Instrucciones de Uso - Procesamiento Masivo
            </h3>
            <ol className="masivo-instructionList">
              <li>Selecciona la <strong>carpeta principal</strong> que contiene todas las subcarpetas y/o archivos ZIP</li>
              <li>Haz clic en <strong>"Iniciar Procesamiento"</strong></li>
              <li>El sistema escaneará automáticamente todos los elementos procesables</li>
              <li>Al finalizar, busca el archivo <code>excel_con_resultados.zip</code> en la carpeta principal</li>
              <li>Extrae el ZIP para acceder a todos los archivos Excel generados</li>
            </ol>
          </div>

          {/* FORMATOS DE ENTRADA */}
          <div className="masivo-infoSection">
            <h3 className="masivo-sectionHeader">
              <FaFolder className="masivo-stepIcon" />
              Formatos de Entrada Soportados
            </h3>
            <div className="masivo-supportedFormats">
              <div className="masivo-formatItem">
                <strong>📁 Carpetas:</strong> Cualquier carpeta que contenga archivos PDF (incluyendo subcarpetas)
              </div>
              <div className="masivo-formatItem">
                <strong>📦 Archivos ZIP:</strong> Comprimidos que contengan PDFs en su interior
              </div>
              <div className="masivo-formatItem">
                <strong>🔄 Procesamiento Recursivo:</strong> Busca PDFs en todos los niveles de subdirectorios
              </div>
            </div>
          </div>

          {/* CONSIDERACIONES TÉCNICAS */}
          <div className="masivo-warningSection">
            <h4 className="masivo-warningTitle">🔧 Consideraciones Técnicas Importantes</h4>
            <ul className="masivo-warningList">
              <li>El procesamiento es <strong>no bloqueante</strong> - puedes continuar usando la aplicación</li>
              <li>Los archivos temporales se <strong>limpian automáticamente</strong> después del procesamiento</li>
              <li>El tiempo total depende de la <strong>cantidad de elementos y PDFs</strong> a procesar</li>
              <li>Requiere <strong>conexión estable</strong> al backend durante todo el proceso</li>
              <li>Los PDFs deben ser de <strong>texto seleccionable</strong> para una extracción óptima</li>
            </ul>
          </div>

        </div>
      </div>
    </div>
  )
}