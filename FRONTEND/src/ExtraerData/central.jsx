import { useState } from "react";
import MassiveProcessor from "./Componentes/MassiveProcessor";
import NormalProcessor from "./Componentes/NormalProcessor";
import "./central.css";

function Central() {
  const [activeTab, setActiveTab] = useState("normal");

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>ExtraData - Sistema de extraer informacion de PDFS</h1>
        <p>Convierte documentos PDF a datos estructurados en Excel</p>
      </header>

      <div className="tabs-container">
        <div className="tabs">
          <button 
            className={`tab ${activeTab === "normal" ? "active" : ""}`}
            onClick={() => setActiveTab("normal")}
          >
            Procesamiento Individual
          </button>
          <button 
            className={`tab ${activeTab === "massive" ? "active" : ""}`}
            onClick={() => setActiveTab("massive")}
          >
            Procesamiento Masivo
          </button>
        </div>
        
          {activeTab === "normal" ? <NormalProcessor /> : <MassiveProcessor />}
      </div>

      <footer className="app-footer">
        <p>Sistema desarrollado para procesamiento eficiente de documentos</p>
      </footer>
    </div>
  );
}

export default Central;