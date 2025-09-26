import { useState } from "react";
import Swal from "sweetalert2";
import withReactContent from "sweetalert2-react-content";
import { FaInfoCircle, FaFolderOpen, FaHashtag } from "react-icons/fa"; // <-- Agregamos más íconos
import "./processorStyles.css";

const MySwal = withReactContent(Swal);

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

function NormalProcessor() {
  const [ruta, setRuta] = useState("");
  const [ficha, setFicha] = useState("");
  const [loading, setLoading] = useState(false);

  const handleProcesar = async () => {
    if (!API_BASE_URL) {
      MySwal.fire({
        icon: "error",
        title: "Error de configuración",
        text: "La URL del backend no está configurada",
        confirmButtonColor: "#16a34a",
      });
      return;
    }

    setLoading(true);

    MySwal.fire({
      title: "Procesando...",
      text: "Por favor espera mientras se procesan los documentos",
      allowOutsideClick: false,
      showConfirmButton: false,
      background: "#f8fafc",
      customClass: {
        popup: "custom-swal",
      },
      didOpen: () => {
        Swal.showLoading();
      },
    });

    try {
      const response = await fetch(`${API_BASE_URL}/procesar`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Accept: "application/json",
        },
        body: JSON.stringify({ ruta, ficha }),
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Error ${response.status}: ${errorText}`);
      }

      const data = await response.json();

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
        confirmButtonColor: "#16a34a",
        customClass: {
          popup: "custom-swal",
        },
      }).then(() => {
        setRuta("");
        setFicha("");
      });
    } catch (err) {
      console.error("Error en la solicitud:", err);
      Swal.fire({
        icon: "error",
        title: "Error en el procesamiento",
        text: err.message,
        confirmButtonColor: "#16a34a",
        customClass: {
          popup: "custom-swal",
        },
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card-container green-card">
      <h2 className="card-title green">ExtraerData</h2>
      <div className="card-icons">
        <FaInfoCircle className="icon green" />
      </div>

      <div className="input-box">
        <label className="input-label">
          <FaFolderOpen className="label-icon green" />
          Ruta de la carpeta o zip
        </label>
        <input
          type="text"
          value={ruta}
          onChange={(e) => setRuta(e.target.value)}
          placeholder="Ingresa la ruta de la carpeta"
          className="input-field"
          disabled={loading}
        />
      </div>

      <div className="input-box">
        <label className="input-label">
          <FaHashtag className="label-icon green" />
          Número de ficha
        </label>
        <input
          type="text"
          value={ficha}
          onChange={(e) => setFicha(e.target.value)}
          placeholder="Ingresa el numero de la ficha"
          className="input-field"
          disabled={loading}
        />
      </div>

      <button
        onClick={handleProcesar}
        disabled={loading || !ruta}
        className="btn-green"
      >
        {loading ? "Procesando..." : "Iniciar Procesamiento"}
      </button>
    </div>
  );
}

export default NormalProcessor;
