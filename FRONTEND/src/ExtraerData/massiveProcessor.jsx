import { useState, useEffect } from "react";
import Swal from "sweetalert2";
import { FaFolderOpen, FaInfoCircle } from "react-icons/fa";
import "./processorStyles.css";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

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
    if (!API_BASE_URL) {
      Swal.fire({
        icon: "error",
        title: "Error de configuración",
        text: "La URL del backend no está configurada.",
        confirmButtonColor: "#7c3aed",
      });
      return;
    }

    if (!ruta) {
      Swal.fire({
        icon: "warning",
        title: "Ruta no encontrada",
        text: "Por favor, ingresa una ruta válida antes de continuar.",
        confirmButtonColor: "#7c3aed",
      });
      return;
    }

    // ✅ Alerta previa: muestra la ruta y espera confirmación del usuario
    await Swal.fire({
      icon: "success",
      title: "Carpeta encontrada",
      text: `La carpeta se detectó exitosamente. Presiona Aceptar para iniciar el proceso.`,
      confirmButtonText: "Aceptar",
      confirmButtonColor: "#7c3aed",
      customClass: {
        popup: "custom-swal",
      },
    });

    // Solo después de que el usuario presione "Aceptar" inicia el procesamiento
    setLoading(true);
    setStatus(null);
    setProgress(0);
    setResult(null);

    const newProcessId = generateProcessId();
    setProcessId(newProcessId);

    try {
      const response = await fetch(`${API_BASE_URL}/procesar-masivo`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ruta, process_id: newProcessId }),
      });

      const data = await response.json();
      if (!response.ok)
        throw new Error(
          data.error || "Error al iniciar el procesamiento masivo"
        );

      iniciarPolling(newProcessId);
    } catch (err) {
      setLoading(false);
      Swal.fire({
        icon: "error",
        title: "Error",
        text: err.message,
        confirmButtonColor: "#7c3aed",
      });
    }
  };

  const iniciarPolling = (id) => {
    if (pollingInterval) clearInterval(pollingInterval);

    const interval = setInterval(async () => {
      try {
        const statusResponse = await fetch(
          `${API_BASE_URL}/procesar-masivo/status/${id}`
        );
        const statusData = await statusResponse.json();

        setStatus(statusData);
        setProgress(statusData.progress || 0);

        if (["completed", "error", "cancelled"].includes(statusData.status)) {
          clearInterval(interval);
          setLoading(false);

          if (statusData.status === "completed") {
            const resultResponse = await fetch(
              `${API_BASE_URL}/procesar-masivo/result/${id}`
            );
            const resultData = await resultResponse.json();
            setResult(resultData);

            Swal.fire({
              icon: "success",
              title: "Procesamiento completado",
              text: "Los resultados se guardan en la misma carpeta seleccionada.",
              confirmButtonColor: "#7c3aed",
              customClass: {
                popup: "custom-swal",
              },
            }).then(() => {
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
              confirmButtonColor: "#7c3aed",
            });
          } else if (statusData.status === "cancelled") {
            Swal.fire({
              icon: "info",
              title: "Proceso cancelado",
              text: "El procesamiento fue detenido.",
              confirmButtonColor: "#7c3aed",
            });
          }
        }
      } catch (err) {
        console.error("Error en polling:", err);
        Swal.fire({
          icon: "error",
          title: "Error en conexión",
          text: "No se pudo obtener el estado del proceso",
          confirmButtonColor: "#7c3aed",
        });
      }
    }, 2000);

    setPollingInterval(interval);
  };

  useEffect(() => {
    return () => {
      if (pollingInterval) clearInterval(pollingInterval);
    };
  }, [pollingInterval]);

  return (
    <div className="card-container purple-card">
      <h2 className="card-title purple-title">ExtraerData</h2>
      <div className="card-icons">
        <FaInfoCircle className="icon purple" />
      </div>

      <div className="input-box">
        <label className="input-label">
          <FaFolderOpen className="label-icon purple" />
          Ruta de la carpeta principal
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

      <button
        onClick={iniciarProcesamiento}
        disabled={loading || !ruta}
        className={`btn-purple ${loading ? "btn-processing" : ""}`}
      >
        {loading ? "Procesando..." : "Iniciar Procesamiento"}
      </button>

    </div>
  );
}

export default MassiveProcessor;