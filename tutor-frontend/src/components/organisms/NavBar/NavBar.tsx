import React, {
  useState,
  useEffect,
  useRef,
} from "react";
import { useAuth } from "@context/auth/AuthContext";
import Sidebar     from "@components/organisms/Sidebar/Sidebar";

import styles from "./Navbar.module.css";


const Navbar: React.FC = () => {
  const { isAuthenticated, user, loading: authLoading } = useAuth();

  /** -------- estado -------- */
  // userData and loadingUser states are removed
  const [sidebarOpen, setSidebarOpen] = useState(false);

  /** -------- ref del botón hamburguesa (opener) -------- */
  const openerRef = useRef<HTMLButtonElement | null>(null);

  /** -------- body class cuando el sidebar está abierto ------- */
  useEffect(() => {
    document.body.classList.toggle("sidebar-open", sidebarOpen);
    return () => document.body.classList.remove("sidebar-open");
  }, [sidebarOpen]);


  /* ---------- loader ---------- */
  if (authLoading) {
    return <nav className={styles.nav}><div>Cargando...</div></nav>; 
  }

  /* ---------- NAVBAR PÚBLICO ---------- */
  if (!isAuthenticated || !user) {
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

  /* ---------- NAVBAR PRIVADO ---------- */
  return (
    <>
      <Sidebar
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
        openerRef={openerRef}
      />

      <nav className={styles.nav}>
        <button
          ref={openerRef}
          className={styles.menuButton}
          onClick={() => setSidebarOpen(o => !o)}
          aria-label="Abrir menú lateral"
        >
          <span className={styles.hamburger} />
          <span className={styles.hamburger} />
          <span className={styles.hamburger} />
        </button>

        <span className={styles.brand}>Tutor Virtual</span>

        <div className={styles.userSection}>
          <span className={styles.welcome}>
            ¡Hola, {user?.username ?? "Usuario"}! 
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