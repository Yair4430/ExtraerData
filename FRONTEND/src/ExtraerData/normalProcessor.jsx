import { useState } from "react";
import Swal from "sweetalert2";
import withReactContent from "sweetalert2-react-content";
import "./processorStyles.css";

const MySwal = withReactContent(Swal);

// Obtener la URL base desde las variables de entorno
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL;

function NormalProcessor() {
  const [ruta, setRuta] = useState("");
  const [ficha, setFicha] = useState("");
  const [loading, setLoading] = useState(false);

  const handleProcesar = async () => {
    setLoading(true);

    MySwal.fire({
      title: "Procesando...",
      text: "Por favor espera mientras se procesan los documentos",
      allowOutsideClick: false,
      showConfirmButton: false,
      background: '#f8fafc',
      customClass: {
        popup: 'custom-swal'
      },
      didOpen: () => {
        Swal.showLoading();
      },
    });

    try {
      const response = await fetch(`${API_BASE_URL}/procesar`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ruta, ficha }),
      });

      const data = await response.json();
      if (!response.ok) throw new Error(data.error || `Error ${response.status}: ${response.statusText}`);

      // ✅ Mostrar resultado en SweetAlert2 y limpiar al aceptar
      Swal.fire({
        icon: "success",
        title: "Procesamiento exitoso",
        html: `
          <div class="result-display">
            <p>${data.message}</p>
            <div class="result-details">
              <p><strong>Documentos procesados:</strong> ${data.documentos_procesados}</p>
              <p><strong>Excel generado en:</strong> ${data.excel_path}</p>
            </div>
          </div>
        `,
        confirmButtonColor: "#4f46e5",
        customClass: {
          popup: 'custom-swal'
        }
      }).then(() => {
        // 🔄 Limpiar campos después de dar "Aceptar"
        setRuta("");
        setFicha("");
      });
    } catch (err) {
      Swal.fire({
        icon: "error",
        title: "Error en el procesamiento",
        text: err.message,
        confirmButtonColor: "#4f46e5",
        customClass: {
          popup: 'custom-swal'
        }
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="processor-container">
      <div className="processor-header">
        <h2>Procesamiento Individual</h2>
        <p>Procesa carpetas o archivos ZIP con documentos PDF de forma individual</p>
      </div>

      <div className="processor-form">
        <div className="form-group">
          <label className="form-label">Ruta de la carpeta o zip:</label>
          <div className="input-container">
            <input
              type="text"
              value={ruta}
              onChange={(e) => setRuta(e.target.value)}
              placeholder="Ej: C:/Users/MiUsuario/Downloads/archivos.zip"
              className="form-input"
              disabled={loading}
            />
            <span className="input-icon">📁</span>
          </div>
        </div>

        <div className="form-group">
          <label className="form-label">Numero de ficha:</label>
          <div className="input-container">
            <input
              type="text"
              value={ficha}
              onChange={(e) => setFicha(e.target.value)}
              placeholder="Ej: 2671143"
              className="form-input"
              disabled={loading}
            />
            <span className="input-icon">🔢</span>
          </div>
        </div>

        <div className="form-actions">
          <button
            onClick={handleProcesar}
            disabled={loading || !ruta}
            className="btn btn-primary"
          >
            {loading ? (
              <>
                <span className="spinner"></span>
                Procesando...
              </>
            ) : (
              "Iniciar Procesamiento"
            )}
          </button>
        </div>
      </div>
    </div>
  );
}

export default NormalProcessor;