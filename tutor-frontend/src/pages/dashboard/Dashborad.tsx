// src/pages/Dashboard.tsx
import React from "react";
import { useAuth } from "../../context/AuthContext";
import { useNavigate } from "react-router-dom";
import styles from "./Dashboard.module.css";

const Dashboard: React.FC = () => {
  const { logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/");
  };

  return (
    <div className={styles.dashboardContainer}>
      <h1>Bienvenido al Dashboard</h1>
      <p>Aquí podrás ver tu progreso, ejercicios recomendados y mucho más.</p>

      <div className={styles.actions}>
        <button onClick={() => alert("Progreso próximamente")}>
          Ver Progreso 📊
        </button>
        <button onClick={() => alert("Ejercicios próximamente")}>
          Ir a Ejercicios 🧠
        </button>
        <button onClick={handleLogout} className={styles.logout}>
          Cerrar Sesión 🔒
        </button>
      </div>
    </div>
  );
};

export default Dashboard;
