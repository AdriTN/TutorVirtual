import {
  memo,
  useEffect,
  useMemo,
  useRef,
  type RefObject,
} from "react";
import { NavLink } from "react-router-dom";
import {
  FiHome,
  FiBookOpen,
  FiBarChart2,
  FiCalendar,
  FiShield,
} from "react-icons/fi";
import { FaMagnifyingGlass } from "react-icons/fa6";

import { useAuth } from "@context/auth/AuthContext";
import styles     from "./Sidebar.module.css";

interface Props {
  isOpen:   boolean;
  onClose(): void;
  openerRef: RefObject<HTMLElement | null>;
}

const Sidebar = ({ isOpen, onClose, openerRef }: Props) => {
  const { isAdmin } = useAuth();

  /* ---------- 1. Lista de enlaces ---------- */
  const items = useMemo(
    () => [
      { to: "/dashboard",  icon: FiHome,           label: "Dashboard" },
      { to: "/my-courses", icon: FiBookOpen,       label: "Mis cursos" },
      { to: "/stats",      icon: FiBarChart2,      label: "Estadísticas" },
      { to: "/courses",    icon: FaMagnifyingGlass,label: "Explorar" },
      { to: "/calendar",   icon: FiCalendar,       label: "Calendario" },
      ...(isAdmin
        ? [{ to: "/admin", icon: FiShield, label: "Panel admin" }]
        : []),
    ],
    [isAdmin],
  );

  /* ---------- 2. Gestión de foco ---------- */
  const firstLinkRef = useRef<HTMLAnchorElement | null>(null);

  useEffect(() => {
    if (isOpen) {
      firstLinkRef.current?.focus();
    } else {
      openerRef.current?.focus();
    }
  }, [isOpen, openerRef]);

  /* ---------- 3. Cerrar con ESC ---------- */
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape" && isOpen) onClose();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [isOpen, onClose]);

  /* ---------- 4. Render ---------- */
  return (
    <aside
      className={`${styles.sidebar} ${isOpen ? styles.open : ""}`}
      inert={!isOpen ? false : undefined}
      aria-hidden={!isOpen}
    >
      <header className={styles.header}>
        <button
          type="button"
          className={styles.menuButton}
          onClick={onClose}
          aria-label="Cerrar menú lateral"
        >
          <span className={styles.hamburger} />
          <span className={styles.hamburger} />
          <span className={styles.hamburger} />
        </button>
        <span className={styles.brand}>Tutor Virtual</span>
      </header>

      <nav className={styles.nav} aria-label="Menú principal">
        <ul className={styles.menu}>
          {items.map(({ to, icon: Icon, label }, idx) => (
            <li key={to} className={styles.menuItem}>
              <NavLink
                ref={idx === 0 ? firstLinkRef : undefined}
                to={to}
                className={({ isActive }) =>
                  `${styles.menuLink} ${isActive ? styles.active : ""}`
                }
                onClick={onClose}
              >
                <Icon className={styles.menuIcon} />
                {label}
              </NavLink>
            </li>
          ))}
        </ul>
      </nav>
    </aside>
  );
};

export default memo(Sidebar);
