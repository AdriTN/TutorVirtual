import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  FiHome,
  FiBookOpen,
  FiBarChart2,
  FiAward,
  FiCalendar,
} from 'react-icons/fi';
import styles from './Sidebar.module.css';

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
}

const Sidebar: React.FC<SidebarProps> = ({ isOpen, onClose }) => (
  <aside className={`${styles.sidebar} ${isOpen ? styles.open : ''}`}>
    <div className={styles.header}>
      <button className={styles.menuButton} onClick={onClose} aria-label="Cerrar sidebar">
        <span className={styles.hamburger} />
        <span className={styles.hamburger} />
        <span className={styles.hamburger} />
      </button>
      <span className={styles.brand}>Tutor Virtual</span>
    </div>
    <ul className={styles.menu}>
      {[
        { to: '/dashboard', icon: FiHome, label: 'Dashboard' },
        { to: '/courses', icon: FiBookOpen, label: 'Mis Cursos' },
        { to: '/statistics', icon: FiBarChart2, label: 'Estadísticas' },
        { to: '/achievements', icon: FiAward, label: 'Logros' },
        { to: '/calendar', icon: FiCalendar, label: 'Calendario' },
      ].map(({ to, icon: Icon, label }) => (
        <li key={to} className={styles.menuItem}>
          <NavLink
            to={to}
            className={({ isActive }) =>
              isActive
                ? `${styles.menuLink} ${styles.active}`
                : styles.menuLink
            }
          >
            <Icon className={styles.menuIcon} />
            {label}
          </NavLink>
        </li>
      ))}
    </ul>
  </aside>
);

export default Sidebar;
