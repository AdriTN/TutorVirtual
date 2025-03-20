import React from "react";
import styles from "./Footer.module.css";

const Footer: React.FC = () => {
  return (
    <footer className={styles.footerContainer}>
      <div className={styles.footerLinks}>
        <a href="/ayuda" className={styles.footerLink}>Ayuda</a>
        <a href="/contacto" className={styles.footerLink}>Contacto</a>
        <a href="/privacidad" className={styles.footerLink}>Política de Privacidad</a>
      </div>
      <div className={styles.footerCopy}>
        © {new Date().getFullYear()} Tutor Virtual. Todos los derechos reservados.
      </div>
    </footer>
  );
};

export default Footer;
