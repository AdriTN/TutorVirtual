// src/pages/dashboard/Dashboard.tsx
import React, { useEffect, useState } from "react";
import { useAuth } from "../../context/AuthContext";
import { useNavigate } from "react-router-dom";
import styles from "./Dashboard.module.css";
import { api } from "../../services/apis/backend-api/api";
import NavBar from "../utils/NavBar/NavBar";

interface UserData {
  id: number;
  name: string;
  email: string;
}

const Dashboard: React.FC = () => {
  const { logout } = useAuth();
  const navigate = useNavigate();

  // Estado para guardar los datos del usuario
  const [userData, setUserData] = useState<UserData | null>(null);
  const [loadingUser, setLoadingUser] = useState(true);

  // Al montar el componente, llamamos a GET /api/users/me
  useEffect(() => {
    const fetchUserData = async () => {
      try {
        // Ajusta la URL según tu prefix ("/api/users/me")
        const response = await api.get("/api/users/me");
        setUserData(response.data); // { id, name, email }
      } catch (error) {
        console.error("Error al obtener datos del usuario:", error);
      } finally {
        setLoadingUser(false);
      }
    };

    fetchUserData();
  }, []);

  const handleLogout = () => {
    logout();
    navigate("/");
  };

  // Mientras obtenemos los datos del usuario
  if (loadingUser) {
    return <div>Cargando datos del usuario...</div>;
  }

  return (
    <>
    <NavBar/>
    <div className={styles.dashboardContainer}>
      <h1>Bienvenido al Dashboard</h1>

      {/* Si ya tenemos los datos, los mostramos */}
      {userData && (
        <p>
          ¡Hola <strong>{userData.name}</strong>! Tu correo es:{" "}
          <strong>{userData.email}</strong>
        </p>
      )}

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
    </>
  );
};

export default Dashboard;
