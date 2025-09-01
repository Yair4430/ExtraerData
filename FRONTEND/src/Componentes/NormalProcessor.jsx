import { useState } from "react";
import "./ProcessorStyles.css";

function NormalProcessor() {
  const [ruta, setRuta] = useState("");
  const [ficha, setFicha] = useState("");
  const [loading, setLoading] = useState(false);
  const [resultado, setResultado] = useState(null);
  const [error, setError] = useState(null);

  const handleProcesar = async () => {
    setLoading(true);
    setError(null);
    setResultado(null);

    try {
      const response = await fetch("http://127.0.0.1:5000/procesar", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ruta, ficha }),
      });

      const data = await response.json();
      if (!response.ok) throw new Error(data.error || `Error ${response.status}: ${response.statusText}`);

      setResultado(data);
    } catch (err) {
      setError(err.message);
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
            placeholder="C:/Users/Yair/Downloads/archivos.zip"
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

      {error && <div className="error-message">{error}</div>}

      {resultado && (
        <div className="result-container result-success">
          <p className="result-title">{resultado.message}</p>
          <p>Documentos procesados: {resultado.documentos_procesados}</p>
          <p>Excel generado en: {resultado.excel_path}</p>
        </div>
      )}
    </div>
  );
}

export default NormalProcessor;
