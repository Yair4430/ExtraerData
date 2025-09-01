import React, { useState } from "react";
import NormalProcessor from "./Componentes/NormalProcessor";
import MassiveProcessor from "./Componentes/MassiveProcessor";
import "./App.css";

function App() {
  const [activeTab, setActiveTab] = useState("normal");

  return (
    <div className="app">
      <header className="app-header">
        <h1>Extractor de Datos de PDF</h1>
      </header>

      <nav className="tabs">
        <button
          className={activeTab === "normal" ? "active" : ""}
          onClick={() => setActiveTab("normal")}
        >
          Procesamiento Normal
        </button>
        <button
          className={activeTab === "masivo" ? "active" : ""}
          onClick={() => setActiveTab("masivo")}
        >
          Procesamiento Masivo
        </button>
      </nav>

      <main className="main-content">
        {activeTab === "normal" && <NormalProcessor />}
        {activeTab === "masivo" && <MassiveProcessor />}
      </main>
    </div>
  );
}

export default App;
