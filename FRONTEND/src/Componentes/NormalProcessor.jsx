import { useState } from "react";
import Swal from "sweetalert2";
import withReactContent from "sweetalert2-react-content";
import "./ProcessorStyles.css";

const MySwal = withReactContent(Swal);

function NormalProcessor() {
  const [ruta, setRuta] = useState("");
  const [ficha, setFicha] = useState("");
  const [loading, setLoading] = useState(false);

  const handleProcesar = async () => {
    setLoading(true);

    MySwal.fire({
      title: "🚀 Procesando...",
      text: "Por favor espera mientras se procesan los documentos",
      allowOutsideClick: false,
      showConfirmButton: false,
      didOpen: () => {
        Swal.showLoading();
      },
    });

    try {
      const response = await fetch("http://127.0.0.1:5000/procesar", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ruta, ficha }),
      });

      const data = await response.json();
      if (!response.ok) throw new Error(data.error || `Error ${response.status}: ${response.statusText}`);

      // ✅ Mostrar resultado en SweetAlert2 y limpiar al aceptar
      Swal.fire({
        icon: "success",
        title: "✅ Procesamiento exitoso",
        html: `
          <p style="font-size:1rem; margin-bottom:10px;">${data.message}</p>
          <p><strong>📄 Documentos procesados:</strong> ${data.documentos_procesados}</p>
          <p><strong>📊 Excel generado en:</strong> ${data.excel_path}</p>
        `,
        confirmButtonColor: "#16a34a",
      }).then(() => {
        // 🔄 Limpiar campos después de dar "Aceptar"
        setRuta("");
        setFicha("");
      });
    } catch (err) {
      Swal.fire({
        icon: "error",
        title: "❌ Error en el procesamiento",
        text: err.message,
        confirmButtonColor: "#dc2626",
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="processor-container">
      <h1 className="processor-title">Procesar Documentos PDF</h1>

      <div className="processor-form">
        <div className="form-group">
          <label className="form-label">Ruta del archivo o carpeta</label>
          <input
            type="text"
            value={ruta}
            onChange={(e) => setRuta(e.target.value)}
            placeholder="C:/Users/Juanito/Downloads/archivos.zip"
            className="form-input"
            disabled={loading}
          />
        </div>

        <div className="form-group">
          <label className="form-label">Ficha</label>
          <input
            type="text"
            value={ficha}
            onChange={(e) => setFicha(e.target.value)}
            placeholder="2671143"
            className="form-input"
            disabled={loading}
          />
        </div>

        <button
          onClick={handleProcesar}
          disabled={loading || !ruta}
          className="processor-button"
        >
          {loading ? "Procesando..." : "Procesar"}
        </button>
      </div>
    </div>
  );
}

export default NormalProcessor;
