import { useState } from "react"
import { AnimatePresence, motion } from "framer-motion"
import MassiveProcessor from "./Masivo/massiveProcessor"
import NormalProcessor from "./Normal/normalProcessor"
import "./central.css"

function Central() {
  // ESTADOS PRINCIPALES: Controlan el modo de operación y el estado de carga
  const [modo, setModo] = useState("normal")
  const [isLoadingNormal, setIsLoadingNormal] = useState(false)
  const [isLoadingMasivo, setIsLoadingMasivo] = useState(false)

  // VERIFICACIÓN DE PROCESAMIENTO: Evita cambios durante operaciones activas
  const isAnyProcessing = isLoadingNormal || isLoadingMasivo

  // MANEJADOR DE CAMBIO DE MODO: Permite alternar entre normal y masivo
  const handleModeSwitch = () => {
    if (!isAnyProcessing) {
      setModo(modo === "normal" ? "masivo" : "normal")
    }
  }

  return (
    <div className="App">
      {/* SWITCH ANIMADO: Interfaz para cambiar entre modos con feedback visual */}
      <motion.div
        className={`switch ${modo} ${isAnyProcessing ? "disabled" : ""}`}
        onClick={handleModeSwitch}
        whileTap={!isAnyProcessing ? { scale: 0.9 } : {}} // Solo anima si no hay procesamiento activo
        style={{
          opacity: isAnyProcessing ? 0.5 : 1,
          cursor: isAnyProcessing ? "not-allowed" : "pointer",
        }}
      >
        <motion.div
          layout
          transition={{ type: "spring", stiffness: 500, damping: 30 }}
          className={`switch-slider ${modo}`}
        >
          {/* ANIMACIÓN DE TEXTO: Transición suave entre "Normal" y "Masivo" */}
          <AnimatePresence mode="wait">
            <motion.span
              key={modo}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.3 }}
            >
              {modo === "normal" ? "Normal" : "Masivo"}
            </motion.span>
          </AnimatePresence>
        </motion.div>
      </motion.div>

      {/* CONTENIDO DINÁMICO: Renderiza el componente correspondiente al modo activo */}
      <AnimatePresence mode="wait">
        <motion.div
          key={modo}
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.95 }}
          transition={{ duration: 0.6, ease: "easeInOut" }}
          className="contenido"
        >
          {/* COMPONENTE CONDICIONAL: Muestra CertiNormal o CertiMasivo según el modo */}
          {modo === "normal" ? (
            <NormalProcessor isLoading={isLoadingNormal} setIsLoading={setIsLoadingNormal} />
          ) : (
            <MassiveProcessor isLoading={isLoadingMasivo} setIsLoading={setIsLoadingMasivo} />
          )}
        </motion.div>
      </AnimatePresence>
    </div>
  )
}

export default Central