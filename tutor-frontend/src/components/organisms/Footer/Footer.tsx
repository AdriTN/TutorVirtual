import React from "react";
import {
  Mail,
  Phone,
  Github,
  Linkedin,
  Twitter,
} from "lucide-react";

import styles from "./Footer.module.css";

const Footer: React.FC = () => {
  const year = new Date().getFullYear();

  return (
    <footer className={styles.footerContainer}>
      <div className={styles.footerGrid}>
        {/* ─── Brand ───────────────────────────────────────────── */}
        <div>
          <h3 className={styles.brandTitle}>Tutor Virtual</h3>
          <p className={styles.brandTagline}>
            Aprender nunca fue tan sencillo. Plataformas, recursos y tutores en
            un mismo lugar.
          </p>
        </div>

        {/* ─── Navegación rápida ──────────────────────────────── */}
        <nav className={styles.navColumn} aria-label="Navegación">
          <h4 className={styles.colTitle}>Explorar</h4>
          <a className={styles.footerLink} href="/cursos">Cursos</a>
          <a className={styles.footerLink} href="/tutores">Tutores</a>
          <a className={styles.footerLink} href="/blog">Blog</a>
          <a className={styles.footerLink} href="/precios">Precios</a>
        </nav>

        {/* ─── Recursos de ayuda ──────────────────────────────── */}
        <nav className={styles.navColumn} aria-label="Ayuda">
          <h4 className={styles.colTitle}>Ayuda</h4>
          <a className={styles.footerLink} href="/faq">Preguntas frecuentes</a>
          <a className={styles.footerLink} href="/contacto">
            <Mail size={16} /> Contacto
          </a>
          <a className={styles.footerLink} href="/soporte">
            <Phone size={16} /> Soporte
          </a>
        </nav>

        {/* ─── Legal / Social ─────────────────────────────────── */}
        <div className={styles.navColumn}>
          <h4 className={styles.colTitle}>Legal</h4>
          <a className={styles.footerLink} href="/privacidad">Privacidad</a>
          <a className={styles.footerLink} href="/terminos">Términos</a>

          <div className={styles.socialRow} aria-label="Redes sociales">
            <a
              className={styles.socialIcon}
              href="https://github.com/tutorvirtual"
              aria-label="GitHub"
            >
              <Github size={18} />
            </a>
            <a
              className={styles.socialIcon}
              href="https://linkedin.com/company/tutorvirtual"
              aria-label="LinkedIn"
            >
              <Linkedin size={18} />
            </a>
            <a
              className={styles.socialIcon}
              href="https://twitter.com/tutorvirtual"
              aria-label="Twitter"
            >
              <Twitter size={18} />
            </a>
          </div>
        </div>
      </div>

      {/* ─── Línea inferior ──────────────────────────────────── */}
      <div className={styles.footerBottom}>
        © {year} Tutor Virtual. Todos los derechos reservados.
      </div>
    </footer>
  );
};

export default Footer;
