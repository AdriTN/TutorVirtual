import { AdminCard, EntityTable } from "@features/admin/components";
import Spinner from "@components/atoms/Spinner/Spinner";
import styles from "../../../pages/AdminDashboard.module.css";
import { AdminDataKind, AdminDataItem } from "@features/admin/hooks/useAdminData";

interface AdminManageTabProps {
  courses: AdminDataItem[];
  subjects: AdminDataItem[];
  themeRows: AdminDataItem[];
  loadingThemes: boolean;
  onEdit: (kind: AdminDataKind, item: AdminDataItem) => void;
  onDelete: (kind: AdminDataKind, id: number, label: string) => void;
}

export function AdminManageTab({
  courses,
  subjects,
  themeRows,
  loadingThemes,
  onEdit,
  onDelete,
}: AdminManageTabProps) {
  return (
    <section id="p3" className={`${styles.container} ${styles.managePanel}`}>
      <AdminCard title="Cursos">
        <EntityTable
          items={courses}
          cols={[
            { key: "title", label: "Título" },
            { key: "description", label: "Descripción" },
          ]}
          onEdit={item => onEdit("course", item)}
          onDelete={item => onDelete("course", item.id, item.title || String(item.id))}
        />
      </AdminCard>

      <AdminCard title="Asignaturas">
        <EntityTable
          items={subjects}
          cols={[
            { key: "name", label: "Nombre" },
            { key: "description", label: "Descripción" },
          ]}
          onEdit={item => onEdit("subject", item)}
          onDelete={item => onDelete("subject", item.id, item.name || String(item.id))}
        />
      </AdminCard>

      <AdminCard title="Temas">
        {loadingThemes
          ? <Spinner size={24} />
          : (
            <EntityTable
              items={themeRows}
              cols={[
                { key: "title", label: "Tema" },
                { key: "subject", label: "Asignatura" },
                { key: "description", label: "Descripción" },
              ]}
              onEdit={item => onEdit("theme", item)}
              onDelete={item => onDelete("theme", item.id, item.title || String(item.id))}
            />
          )}
      </AdminCard>
    </section>
  );
}
