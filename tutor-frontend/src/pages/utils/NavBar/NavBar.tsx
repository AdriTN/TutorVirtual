/* Navbar.tsx */
import React, { useState, useEffect } from "react";
import { useAuth } from "../../../context/AuthContext";
import styles from "./Navbar.module.css";
import Sidebar from "../../../components/sidebar/Sidebar";
import api from "../../../services/apis/backend-api/api";

interface UserData {
  id: number;
  name: string;
  email: string;
}

const Navbar: React.FC = () => {
  const { isAuthenticated } = useAuth();

  const [userData,    setUserData]    = useState<UserData | null>(null);
  const [loadingUser, setLoadingUser] = useState(isAuthenticated);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  /* ── efecto: cargar datos SOLO cuando hay sesión ── */
  useEffect(() => {
    if (!isAuthenticated) {
      setUserData(null);
      setLoadingUser(false);
      return;
    }

    const fetchUserData = async () => {
      try {
        const { data } = await api.get<UserData>("/api/users/me");
        setUserData(data);
      } catch (err) {
        console.error("Error al obtener datos del usuario:", err);
      } finally {
        setLoadingUser(false);
      }
    };

    fetchUserData();
  }, [isAuthenticated]);

  /* ── efecto: toggle clase <body> cuando abre/cierra sidebar ── */
  useEffect(() => {
    document.body.classList.toggle("sidebar-open", sidebarOpen);
    return () => document.body.classList.remove("sidebar-open");
  }, [sidebarOpen]);

  /* ------------ render ---------------- */
  if (loadingUser) {
    return <div>Cargando datos del usuario…</div>;
  }

  /* ----- NAVBAR PÚBLICO ----- */
  if (!isAuthenticated) {
    return (
      <nav className={styles.nav}>
        <div className={styles.logo}>
          <img src="/logo.png" alt="Logo" className={styles.logoImage} />
          <a href="/" className={styles.brand}>Tutor Virtual</a>
        </div>

        <ul className={styles.navLinks}>
          <li><a href="/courses" className={styles.navbarItem}>Cursos</a></li>
          <li><a href="/login"   className={styles.navbarItem}>Iniciar sesión</a></li>
        </ul>
      </nav>
    );
  }

  /* ----- NAVBAR PRIVADO ----- */
  return (
    <>
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      <nav className={styles.nav}>
        <button
          className={styles.menuButton}
          onClick={() => setSidebarOpen(o => !o)}
          aria-label="Toggle sidebar">
          <span className={styles.hamburger} />
          <span className={styles.hamburger} />
          <span className={styles.hamburger} />
        </button>

        <span className={styles.brand}>Tutor Virtual</span>

        <div className={styles.userSection}>
          <span className={styles.welcome}>
            ¡Hola, {userData?.name ?? "Usuario"}!
          </span>
          <img
            src="/default-avatar.jpg"
            alt="Perfil"
            className={styles.profileImg}
          />
        </div>
      </nav>
    </>
  );
};

export default Navbar;
