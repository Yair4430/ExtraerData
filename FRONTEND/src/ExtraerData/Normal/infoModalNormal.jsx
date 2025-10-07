import { FaInfoCircle, FaTimes, FaFilePdf, FaFileExcel, FaDatabase, FaRobot, FaSearch, FaDownload } from "react-icons/fa"
import "./infoModalNormal.css" 

export default function InfoModalNormal({ isOpen, onClose }) {
  if (!isOpen) return null

  return (
    <div className="normal-modalOverlay" onClick={onClose}>
      <div className="normal-modalContent" onClick={(e) => e.stopPropagation()}>
        
        {/* CABECERA DEL MODAL */}
        <div className="normal-modalHeader">
          <h2 className="normal-modalTitle">
            <FaInfoCircle className="normal-modalIcon" />
            ¿Cómo funciona ExtraerData?
          </h2>
          <button className="normal-closeButton" onClick={onClose}>
            <FaTimes />
          </button>
        </div>

        {/* CUERPO PRINCIPAL */}
        <div className="normal-modalBody">
          
          {/* DESCRIPCIÓN GENERAL */}
          <div className="normal-infoSection">
            <h3 className="normal-sectionHeader">
              <FaRobot className="normal-stepIcon" />
              Sistema de Extracción Automatizada
            </h3>
            <p className="normal-infoText">
              ExtraerData es un sistema inteligente que procesa documentos PDF de identificación 
              para extraer automáticamente información estructurada como nombres, números de documento 
              y fechas de expedición, generando archivos Excel listos para usar.
            </p>
          </div>

          {/* TIPOS DE DOCUMENTO SOPORTADOS */}
          <div className="normal-infoSection">
            <h3 className="normal-sectionHeader">
              <FaFilePdf className="normal-stepIcon" />
              Documentos Soportados
            </h3>
            <div className="normal-documentTypes">
              <div className="normal-docType"><strong>CC:</strong> Cédula de Ciudadanía Colombiana</div>
              <div className="normal-docType"><strong>TI:</strong> Tarjeta de Identidad</div>
              <div className="normal-docType"><strong>PPT:</strong> Permiso Por Protección Temporal</div>
              <div className="normal-docType"><strong>CE:</strong> Cédula de Extranjería</div>
            </div>
          </div>

          {/* PROCESO DE EXTRACCIÓN */}
          <div className="normal-infoSection">
            <h3 className="normal-sectionHeader">
              <FaSearch className="normal-stepIcon" />
              Proceso de Extracción
            </h3>
            <div className="normal-processSteps">
              <div className="normal-step">
                <span className="normal-stepNumber">1</span>
                <div className="normal-stepContent">
                  <strong>Detección de PDFs:</strong> Busca recursivamente archivos PDF en la carpeta o ZIP seleccionado
                </div>
              </div>
              <div className="normal-step">
                <span className="normal-stepNumber">2</span>
                <div className="normal-stepContent">
                  <strong>Análisis de Texto:</strong> Extrae el texto de cada PDF usando técnicas avanzadas de OCR
                </div>
              </div>
              <div className="normal-step">
                <span className="normal-stepNumber">3</span>
                <div className="normal-stepContent">
                  <strong>Identificación de Tipo:</strong> Detecta automáticamente el tipo de documento (CC, TI, PPT, CE)
                </div>
              </div>
              <div className="normal-step">
                <span className="normal-stepNumber">4</span>
                <div className="normal-stepContent">
                  <strong>Extracción de Datos:</strong> Aplica patrones específicos para cada tipo de documento
                </div>
              </div>
            </div>
          </div>

          {/* DATOS EXTRAÍDOS */}
          <div className="normal-infoSection">
            <h3 className="normal-sectionHeader">
              <FaDatabase className="normal-stepIcon" />
              Información Extraída
            </h3>
            <div className="normal-dataExtracted">
              <div className="normal-dataItem">• Tipo de documento identificado</div>
              <div className="normal-dataItem">• Número de documento completo</div>
              <div className="normal-dataItem">• Nombres y apellidos del titular</div>
              <div className="normal-dataItem">• Fecha de expedición (día, mes, año)</div>
            </div>
          </div>

          {/* RESULTADOS Y EXPORTACIÓN */}
          <div className="normal-infoSection">
            <h3 className="normal-sectionHeader">
              <FaFileExcel className="normal-stepIcon" />
              Resultados y Exportación
            </h3>
            <div className="normal-resultSection">
              <div className="normal-resultItem">
                <FaDownload className="normal-resultIcon" />
                <div>
                  <strong>Archivo Excel Estructurado:</strong> Los datos se exportan a una plantilla Excel 
                  con formato profesional y validaciones integradas.
                </div>
              </div>
              <div className="normal-resultItem">
                <FaDatabase className="normal-resultIcon" />
                <div>
                  <strong>Validaciones Automáticas:</strong> El Excel incluye listas desplegables y 
                  validaciones para asegurar la calidad de los datos.
                </div>
              </div>
            </div>
          </div>

          {/* INSTRUCCIONES DE USO */}
          <div className="normal-infoSection">
            <h3 className="normal-sectionHeader">
              <FaRobot className="normal-stepIcon" />
              Instrucciones de Uso - Procesamiento Normal
            </h3>
            <ol className="normal-instructionList">
              <li>Ingresa la <strong>ruta de la carpeta</strong> que contiene los PDFs o un archivo ZIP/RAR</li>
              <li>Proporciona el <strong>número de ficha</strong> para identificar el procesamiento</li>
              <li>Haz clic en <strong>"Iniciar Procesamiento"</strong></li>
              <li>El sistema buscará y procesará todos los PDFs encontrados</li>
              <li>Los resultados se guardarán automáticamente en tu carpeta de <strong>Descargas</strong></li>
              <li>Busca el archivo: <code>plantilla_[ficha].xlsx</code></li>
            </ol>
          </div>

          {/* FORMATOS SOPORTADOS */}
          <div className="normal-infoSection">
            <h3 className="normal-sectionHeader">
              <FaFilePdf className="normal-stepIcon" />
              Formatos de Entrada Soportados
            </h3>
            <div className="normal-supportedFormats">
              <div className="normal-formatItem">
                <strong>📁 Carpetas:</strong> Cualquier carpeta que contenga archivos PDF
              </div>
              <div className="normal-formatItem">
                <strong>📦 Archivos ZIP:</strong> Comprimidos que contengan PDFs en su interior
              </div>
              <div className="normal-formatItem">
                <strong>📦 Archivos RAR:</strong> Comprimidos RAR (requiere librería adicional)
              </div>
            </div>
          </div>

          {/* CONSIDERACIONES TÉCNICAS */}
          <div className="normal-warningSection">
            <h4 className="normal-warningTitle">🔧 Consideraciones Técnicas</h4>
            <ul className="normal-warningList">
              <li>Los PDFs deben ser de <strong>texto seleccionable</strong> (no escaneados como imagen)</li>
              <li>El sistema procesa <strong>todos los PDFs</strong> encontrados recursivamente en subcarpetas</li>
              <li>Maneja automáticamente archivos temporales y limpia después del procesamiento</li>
              <li>El tiempo de procesamiento depende de la cantidad y tamaño de los PDFs</li>
              <li>Requiere conexión a internet para la comunicación con el backend</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}