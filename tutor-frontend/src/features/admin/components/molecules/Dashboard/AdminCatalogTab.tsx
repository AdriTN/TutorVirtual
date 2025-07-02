import { AdminCard } from "@features/admin/components";
import styles from "../../../pages/AdminDashboard.module.css";
import { AdminDataKind } from "@features/admin/hooks/useAdminData";

interface AdminCatalogTabProps {
  coursesCount: number;
  subjectsCount: number;
  onOpenCreateModal: (kind: AdminDataKind) => void;
}

export function AdminCatalogTab({
  coursesCount,
  subjectsCount,
  onOpenCreateModal,
}: AdminCatalogTabProps) {
  return (
    <section id="p1" className={`${styles.container} ${styles.grid}`}>
      <AdminCard title={`Cursos (${coursesCount})`}>
        <button onClick={() => onOpenCreateModal("course")}>Nuevo curso</button>
      </AdminCard>

      <AdminCard title={`Asignaturas (${subjectsCount})`}>
        <button onClick={() => onOpenCreateModal("subject")}>Nueva asignatura</button>
      </AdminCard>

      <AdminCard title="Temas (global)">
        <button onClick={() => onOpenCreateModal("theme")}>Nuevo tema</button>
      </AdminCard>
    </section>
  );
}
