import React from "react";
import styles from "./Navbar.module.css";

const Navbar: React.FC = () => {
  return (
    <nav className={styles.nav}>
      <div className={styles.logo}>
        <img
          src="logo.png"
          alt="Logo"
          className={styles.logoImage}
        />
      
      <a href="/" className={styles.brand}>
        Tutor Virtual
      </a>
      </div>
      <ul className={styles.navLinks}>
        <li>
          <a href="/" className={styles.navbarItem}>
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
};

export default Navbar;
