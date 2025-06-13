import React from "react";
import { NavLink } from "react-router-dom";
import {
  FiHome,
  FiBookOpen,
  FiBarChart2,
  FiCalendar,
  FiShield,
} from "react-icons/fi";
import { FaMagnifyingGlass } from "react-icons/fa6";
import styles from "./Sidebar.module.css";

import { useAuth } from "../../context/AuthContext";

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
}

const Sidebar: React.FC<SidebarProps> = ({ isOpen, onClose }) => {
  const { isAdmin }      = useAuth();

  /* --------- menú común a todos los usuarios --------- */
  const items = [
    { to: "/dashboard",    icon: FiHome,           label: "Dashboard" },
    { to: "/my-courses",   icon: FiBookOpen,       label: "Mis Cursos" },
    { to: "/stats",        icon: FiBarChart2,      label: "Estadísticas" },
    { to: "/courses",      icon: FaMagnifyingGlass,label: "Explorar" },
    { to: "/calendar",     icon: FiCalendar,       label: "Calendario" },
  ];

  /* --------- extra para administradores --------- */
  if (isAdmin) {
    items.push(
      { to: "/admin", icon: FiShield, label: "Panel admin" }
    );
  }

  return (
    <aside className={`${styles.sidebar} ${isOpen ? styles.open : ""}`}>
      <div className={styles.header}>
        <button
          className={styles.menuButton}
          onClick={onClose}
          aria-label="Cerrar sidebar"
        >
          <span className={styles.hamburger} />
          <span className={styles.hamburger} />
          <span className={styles.hamburger} />
        </button>
        <span className={styles.brand}>Tutor Virtual</span>
      </div>

      <ul className={styles.menu}>
        {items.map(({ to, icon: Icon, label }) => (
          <li key={to} className={styles.menuItem}>
            <NavLink
              to={to}
              className={({ isActive }) =>
                isActive
                  ? `${styles.menuLink} ${styles.active}`
                  : styles.menuLink
              }
              onClick={onClose}
            >
              <Icon className={styles.menuIcon} />
              {label}
            </NavLink>
          </li>
        ))}
      </ul>
    </aside>
  );
};

export default Sidebar;
