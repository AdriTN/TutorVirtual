import React, { useState, useEffect } from 'react';
import { useAuth } from '../../../context/AuthContext';
import styles from './Navbar.module.css';
import Sidebar from '../../../components/sidebar/Sidebar';
import api from '../../../services/apis/backend-api/api';

interface UserData {
  id: number;
  name: string;
  email: string;
}

const Navbar: React.FC = () => {
  const [userData, setUserData] = useState<UserData | null>(null);
  const [loadingUser, setLoadingUser] = useState(true);
  const { isAuthenticated } = useAuth();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  // Si el sidebar cambia, añadimos/quitan la clase al body
  useEffect(() => {
    document.body.classList.toggle('sidebar-open', sidebarOpen);

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

  }, [sidebarOpen]);

  if (loadingUser) {
    return <div>Cargando datos del usuario...</div>;
  }

  // Versión para usuario **NO** autenticado
  if (!isAuthenticated) {
    return (
      <nav className={styles.nav}>
        <div className={styles.logo}>
          <img src="logo.png" alt="Logo" className={styles.logoImage} />
          <a href="/" className={styles.brand}>
            Tutor Virtual
          </a>
        </div>
        <ul className={styles.navLinks}>
          <li>
            <a href="/courses" className={styles.navbarItem}>
              Cursos
            </a>
          </li>
          <li>
            <a href="/login" className={styles.navbarItem}>
              Iniciar Sesión
            </a>
          </li>
        </ul>
      </nav>
    );
  }

  // Versión para usuario autenticado
  return (
    <>
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
      <nav className={styles.nav}>
        <button
          className={styles.menuButton}
          onClick={() => setSidebarOpen(o => !o)}
          aria-label="Toggle sidebar"
        >
          <span className={styles.hamburger} />
          <span className={styles.hamburger} />
          <span className={styles.hamburger} />
        </button>
        <span className={styles.brand}>Tutor Virtual</span>
        <div className={styles.userSection}>
          <span className={styles.welcome}>¡Hola, {userData?.name || 'Usuario'}!</span>
          <img
          // Si no hay avatar, se muestra una imagen por defecto
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
