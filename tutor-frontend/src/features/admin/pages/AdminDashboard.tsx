import { useState } from "react";

import NavBar from "@components/organisms/NavBar/NavBar";
import Footer from "@components/organisms/Footer/Footer";
import Spinner from "@components/atoms/Spinner/Spinner";
import { TabButton } from "@features/admin/components";

import { useAdminData, AdminDataKind, AdminDataItem } from "@features/admin/hooks/useAdminData";
import { AdminModals } from "../components/molecules/Dashboard/AdminModals";
import { AdminCatalogTab } from "../components/molecules/Dashboard/AdminCatalogTab";
import { AdminLinksTab } from "../components/molecules/Dashboard/AdminLinksTab";
import { AdminManageTab } from "../components/molecules/Dashboard/AdminManageTab";

import styles from "./AdminDashboard.module.css";

export default function AdminDashboard() {
  const adminData = useAdminData();
  const {
    courses, loadingCourses,
    subjects, loadingSubjects,
    allThemes, loadingThemes,
    themeRows,
    courseOpts, subjectOpts,
    openCreateModal,
    openEditModal,
    openConfirmDeleteModal,
  } = adminData;

  const [tab, setTab] = useState<"catalog" | "links" | "manage">("catalog");

  if (loadingCourses || loadingSubjects) {
    return <div className={styles.center}><Spinner size={40} /></div>;
  }

  return (
    <div className={styles.page}>
      <NavBar />

      <main className={styles.main}>
        {/* Tabs */}
        <div className={styles.tabs} role="tablist">
          <TabButton id="t1" label="Catálogo" controls="p1"
            active={tab === "catalog"} onClick={() => setTab("catalog")} />
          <TabButton id="t2" label="Vínculos" controls="p2"
            active={tab === "links"} onClick={() => setTab("links")} />
          <TabButton id="t3" label="Gestionar" controls="p3"
            active={tab === "manage"} onClick={() => setTab("manage")} />
        </div>

        {/* Contenido de las Pestañas */}
        {tab === "catalog" && (
          <AdminCatalogTab
            coursesCount={courses.length}
            subjectsCount={subjects.length}
            onOpenCreateModal={(kind: AdminDataKind) => openCreateModal(kind)}
          />
        )}

        {tab === "links" && (
          <AdminLinksTab
            courses={courses.map(course => ({
              ...course,
              description: course.description ?? undefined,
            }))}
            subjects={subjects}
            allThemes={allThemes}
            courseOpts={courseOpts}
            subjectOpts={subjectOpts}
            adminData={adminData}
          />
        )}

        {tab === "manage" && (
          <AdminManageTab
            courses={courses.map(course => ({
              ...course,
              description: course.description ?? undefined,
            }))}
            subjects={subjects}
            themeRows={themeRows}
            loadingThemes={loadingThemes}
            onEdit={(kind: AdminDataKind, item: AdminDataItem) => openEditModal(kind, item)}
            onDelete={(kind: AdminDataKind, id: number, label: string) => openConfirmDeleteModal(kind, id, label)}
          />
        )}

        {/* Modales (se renderizan fuera del flujo de pestañas para estar disponibles globalmente) */}
        <AdminModals
          adminData={adminData}
          subjectOpts={subjectOpts}
        />

      </main>
      <Footer />
    </div>
  );
}
