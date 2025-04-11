import React from "react";
import styles from "./Navbar.module.css";
import { useNavigate } from "react-router-dom";

const Navbar: React.FC = () => {
  return (
    <nav className={styles.nav}>
      <a href="/" className={styles.brand}>
        Tutor Virtual
      </a>
      <ul className={styles.navLinks}>
        <li>
          <a href="/login" className={styles.navbarItem}>
            Login
          </a>
        </li>
        <li>
            <button 
              className={styles.cta}
              onClick={() => {
                const navigate = useNavigate();
                navigate("/register");
              }} 
            >
              <span>Sign Up</span>
              <svg width="15px" height="10px" viewBox="0 0 13 10" color="#be45e2">
                <path d="M1,5 L11,5" />
                <polyline points="8 1 12 5 8 9" />
              </svg>
            </button>
        </li>
      </ul>
    </nav>
  );
};

export default Navbar;
