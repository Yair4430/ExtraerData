// MassiveProcessor.jsx (versión estandarizada)
import { useState, useEffect } from "react";
import Swal from "sweetalert2";
import "./ProcessorStyles.css";

function MassiveProcessor() {
  const [ruta, setRuta] = useState("");
  const [processId, setProcessId] = useState("");
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState(null);
  const [progress, setProgress] = useState(0);
  const [result, setResult] = useState(null);
  const [pollingInterval, setPollingInterval] = useState(null);

  const generateProcessId = () =>
    `massive_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

  const iniciarProcesamiento = async () => {
    setLoading(true);
    setStatus(null);
    setProgress(0);
    setResult(null);

    Swal.fire({
      title: "Iniciando procesamiento...",
      text: "Por favor espera mientras se validan los archivos",
      allowOutsideClick: false,
      didOpen: () => {
        Swal.showLoading();
      },
      background: '#f8fafc',
      customClass: {
        popup: 'custom-swal'
      }
    });

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
      setLoading(false);
      Swal.fire({
        icon: "error",
        title: "Error",
        text: err.message,
        confirmButtonColor: '#4f46e5'
      });
    }
  };

  const iniciarPolling = (id) => {
    if (pollingInterval) clearInterval(pollingInterval);

    const interval = setInterval(async () => {
      try {
        const statusResponse = await fetch(`http://127.0.0.1:5000/procesar-masivo/status/${id}`);
        const statusData = await statusResponse.json();

        setStatus(statusData);
        setProgress(statusData.progress || 0);

        if (["completed", "error", "cancelled"].includes(statusData.status)) {
          clearInterval(interval);
          setLoading(false);
          
          if (statusData.status === "completed") {
            const resultResponse = await fetch(`http://127.0.0.1:5000/procesar-masivo/result/${id}`);
            const resultData = await resultResponse.json();
            setResult(resultData);

            Swal.fire({
              icon: "success",
              title: "Procesamiento completado",
              text: "Los resultados se guardan en la misma carpeta seleccionada.",
              confirmButtonColor: '#4f46e5',
              customClass: {
                popup: 'custom-swal'
              }
            }).then(() => {
              // 🔄 Resetear estados después de aceptar
              setRuta("");
              setProcessId("");
              setStatus(null);
              setProgress(0);
              setResult(null);
            });
          } else if (statusData.status === "error") {
            Swal.fire({
              icon: "error",
              title: "Error en el procesamiento",
              text: statusData.message || "Ocurrió un error inesperado",
              confirmButtonColor: '#4f46e5'
            });
          } else if (statusData.status === "cancelled") {
            Swal.fire({
              icon: "info",
              title: "Proceso cancelado",
              text: "El procesamiento fue detenido.",
              confirmButtonColor: '#4f46e5'
            });
          }
        }
      } catch (err) {
        console.error("Error en polling:", err);
        Swal.fire({
          icon: "error",
          title: "Error en conexión",
          text: "No se pudo obtener el estado del proceso",
          confirmButtonColor: '#4f46e5'
        });
      }
    }, 2000);

    setPollingInterval(interval);
  };

  const cancelarProcesamiento = () => {
    if (pollingInterval) {
      clearInterval(pollingInterval);
      setPollingInterval(null);
    }
    setLoading(false);
    setStatus({ status: "cancelled" });
    
    Swal.fire({
      icon: "info",
      title: "Proceso cancelado",
      text: "El procesamiento ha sido detenido.",
      confirmButtonColor: '#4f46e5'
    });
  };

  useEffect(() => {
    return () => {
      if (pollingInterval) clearInterval(pollingInterval);
    };
  }, [pollingInterval]);

  return (
    <div className="processor-container">
      <div className="processor-header">
        <h2>Procesamiento Masivo</h2>
        <p>Procesa carpetas o archivos ZIP con documentos PDF de forma masiva</p>
      </div>

      <div className="processor-form">
        <div className="form-group">
          <label className="form-label">Ruta de la carpeta principal:</label>
          <div className="input-container">
            <input
              type="text"
              value={ruta}
              onChange={(e) => setRuta(e.target.value)}
              placeholder="Ej: C:/Users/MiUsuario/Downloads/carpeta_principal"
              className="form-input"
              disabled={loading}
            />
            <span className="input-icon">📂</span>
          </div>
          <p className="form-hint">
            La carpeta debe contener subcarpetas o archivos ZIP con documentos PDF
          </p>
        </div>

        <div className="form-actions">
          <button
            onClick={iniciarProcesamiento}
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

export default MassiveProcessor;