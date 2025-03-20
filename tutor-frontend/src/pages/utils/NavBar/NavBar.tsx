import React from "react";
import { Link } from "react-router-dom"; // o un <a href> si no usas React Router
import styles from "./NavBar.module.css";

interface NavBarProps {
  logoUrl?: string; // opcional, si quieres un logo
  brandName?: string; // nombre de tu marca
  links?: Array<{ label: string; path: string }>;
}

const NavBar: React.FC<NavBarProps> = ({
  logoUrl,
  brandName = "Tutor Virtual",
  links = [
    { label: "Inicio", path: "/" },
    { label: "Cómo Funciona", path: "/how" },
    { label: "Ejercicios", path: "/exercises" },
  ],
}) => {
  return (
    <nav className={styles.navbar}>
      <a href="/" className={styles.brand}>
        {logoUrl && <img src={logoUrl} alt="Logo" className={styles.brandLogo} />}
        {brandName}
      </a>

      <div className={styles.navLinks}>
        {links.map((lnk) => (
          // Si usas React Router, usa <Link to={lnk.path} />
          // Si no, un simple <a href={lnk.path}>
          <Link key={lnk.label} to={lnk.path} className={styles.navLink}>
            {lnk.label}
          </Link>
        ))}
      </div>
    </nav>
  );
};

export default NavBar;
