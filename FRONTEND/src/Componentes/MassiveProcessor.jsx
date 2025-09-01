import { useState, useEffect } from "react";
import "./ProcessorStyles.css";

function MassiveProcessor() {
  const [ruta, setRuta] = useState("");
  const [processId, setProcessId] = useState("");
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState(null);
  const [progress, setProgress] = useState(0);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [pollingInterval, setPollingInterval] = useState(null);

  const generateProcessId = () =>
    `massive_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

  const iniciarProcesamiento = async () => {
    setLoading(true);
    setError(null);
    setStatus(null);
    setProgress(0);
    setResult(null);

    const newProcessId = generateProcessId();
    setProcessId(newProcessId);

    try {
      const response = await fetch("http://127.0.0.1:5000/procesar-masivo", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ruta, process_id: newProcessId }),
      });

      const data = await response.json();
      if (!response.ok) throw new Error(data.error || "Error al iniciar el procesamiento masivo");

      iniciarPolling(newProcessId);
    } catch (err) {
      setError(err.message);
      setLoading(false);
    }
  };

  const iniciarPolling = (id) => {
    if (pollingInterval) clearInterval(pollingInterval);

    const interval = setInterval(async () => {
      try {
        const statusResponse = await fetch(`http://127.0.0.1:5000/procesar-masivo/status/${id}`);
        const statusData = await statusResponse.json();

        if (["completed", "error", "cancelled"].includes(statusData.status)) {
          clearInterval(interval);
          setLoading(false);

          if (statusData.status === "completed") {
            const resultResponse = await fetch(`http://127.0.0.1:5000/procesar-masivo/result/${id}`);
            const resultData = await resultResponse.json();
            setResult(resultData);
          }
        }

        setStatus(statusData);
        setProgress(statusData.progress || 0);
      } catch (err) {
        console.error("Error en polling:", err);
      }
    }, 2000);

    setPollingInterval(interval);
  };

  useEffect(() => {
    return () => {
      if (pollingInterval) clearInterval(pollingInterval);
    };
  }, [pollingInterval]);

  const getStatusClass = () => {
    if (!status) return "";
    switch (status.status) {
      case "completed":
        return "status-completed";
      case "error":
        return "status-error";
      case "cancelled":
        return "status-cancelled";
      default:
        return "status-processing";
    }
  };

  return (
    <div className="processor-container">
      <h1 className="processor-title">Procesamiento Masivo de Documentos</h1>

      <div className="processor-form">
        <div className="form-group">
          <label className="form-label">Ruta de la carpeta principal</label>
          <input
            type="text"
            value={ruta}
            onChange={(e) => setRuta(e.target.value)}
            placeholder="C:/Users/Yair/Downloads/carpeta_principal"
            className="form-input"
            disabled={loading}
          />
          <p className="form-hint">
            La carpeta debe contener subcarpetas o archivos ZIP con documentos PDF
          </p>
        </div>

        <button
          onClick={iniciarProcesamiento}
          disabled={loading || !ruta}
          className="processor-button"
        >
          {loading ? "Procesando..." : "Iniciar Procesamiento Masivo"}
        </button>

        {status && (
          <div className={`status-message ${getStatusClass()}`}>
            <p>{status.message}</p>
            {status.status === "processing" && (
              <p className="form-hint">
                Procesando... Esto puede tomar varios minutos dependiendo de la cantidad de archivos.
              </p>
            )}
          </div>
        )}

        {result && result.status === "error" && (
          <div className="result-container result-error">
            <h3 className="result-title">Error en el Procesamiento</h3>
            <p>{result.error}</p>
          </div>
        )}

        {error && <div className="error-message">{error}</div>}
      </div>
    </div>
  );
}

export default MassiveProcessor;
