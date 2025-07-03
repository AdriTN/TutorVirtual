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
  FiShield,
  FiLogOut, // Importar el icono de logout
} from "react-icons/fi";
import { FaMagnifyingGlass } from "react-icons/fa6";
import { useNavigate } from "react-router-dom"; // Importar useNavigate

import { useAuth } from "@context/auth/AuthContext";
import styles     from "./Sidebar.module.css";

interface Props {
  isOpen:   boolean;
  onClose(): void;
  openerRef: RefObject<HTMLElement | null>;
}

const Sidebar = ({ isOpen, onClose, openerRef }: Props) => {
  const { isAdmin, logout } = useAuth(); // Obtener logout del contexto
  const navigate = useNavigate(); // Hook para la navegación

  const handleLogout = async () => {
    onClose(); // Cerrar el sidebar
    await logout(); // Llama a la función de logout del contexto (que ahora es async)
    navigate("/login"); // Redirigir a la página de login
  };

  /* ---------- 1. Lista de enlaces ---------- */
  const menuItems = useMemo(
    () => [
      { key: "dashboard", to: "/dashboard",  icon: FiHome,           label: "Dashboard" },
      { key: "my-courses", to: "/my-courses", icon: FiBookOpen,       label: "Mis cursos" },
      { key: "stats", to: "/stats",      icon: FiBarChart2,      label: "Estadísticas" },
      { key: "explore", to: "/courses",    icon: FaMagnifyingGlass,label: "Explorar" },
      // { to: "/calendar",   icon: FiCalendar,       label: "Calendario" }, // Calendario parece no implementado
      ...(isAdmin
        ? [{ key: "admin", to: "/admin", icon: FiShield, label: "Panel admin" }]
        : []),
    ],
    [isAdmin],
  );

  const bottomMenuItems = useMemo(() => [
    { key: "logout", icon: FiLogOut, label: "Cerrar Sesión", action: handleLogout }
  ], [handleLogout]);


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
          {menuItems.map(({ key, to, icon: Icon, label }, idx) => (
            <li key={key} className={styles.menuItem}>
              <NavLink
                ref={idx === 0 ? firstLinkRef : undefined}
                to={to!} // to puede ser undefined si es un botón de acción, pero NavLink lo requiere
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
        {/* Sección inferior para el botón de logout */}
        <ul className={`${styles.menu} ${styles.bottomMenu}`}>
          {bottomMenuItems.map(({ key, icon: Icon, label, action }) => (
            <li key={key} className={styles.menuItem}>
              <button
                type="button"
                className={styles.menuLink} // Reutilizar estilo de enlace para consistencia
                onClick={action}
              >
                <Icon className={styles.menuIcon} />
                {label}
              </button>
            </li>
          ))}
        </ul>
      </nav>
    </aside>
  );
};

export default memo(Sidebar);
