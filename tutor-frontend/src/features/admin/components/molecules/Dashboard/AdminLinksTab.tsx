import { useState, useMemo } from "react";
import { AdminCard, SelectField, MultiCheckList } from "@features/admin/components";
import Spinner from "@components/atoms/Spinner/Spinner";
import styles from "../../../pages/AdminDashboard.module.css";
import { useAdminData, AdminDataItem } from "@features/admin/hooks/useAdminData";
import { useThemes } from "@features/admin/hooks/useThemes";

interface AdminLinksTabProps {
  courses: AdminDataItem[];
  subjects: AdminDataItem[];
  allThemes: AdminDataItem[];
  courseOpts: { id: number; label: string }[];
  subjectOpts: { id: number; label: string }[];
  adminData: ReturnType<typeof useAdminData>;
}

export function AdminLinksTab({
  courses,
  subjects,
  allThemes,
  courseOpts,
  subjectOpts,
  adminData,
}: AdminLinksTabProps) {
  const {
    addSubjectToCourse,
    detachSubjectsFromCourse,
    addThemeToSubject,
    detachThemesFromSubject,
  } = adminData;

  /* ───── VÍNCULO Curso ↔ Asignatura ───── */
  const [courseId, setCourseId] = useState("");
  const [subjAddId, setSubjAddId] = useState("");
  const [subjDelIds, setSubjDelIds] = useState<number[]>([]);

  const courseSel = courses.find(c => c.id === +courseId);
  const inCourseSubjects = courseSel?.subjects ?? [];
const subjToAdd: AdminDataItem[] = subjects.filter((s: AdminDataItem) => 
    !inCourseSubjects.some((i: AdminDataItem) => i.id === s.id)
);
  const subjToDel = inCourseSubjects;

  const handleAddSubjectToCourse = () => {
    if (courseId && subjAddId) {
      addSubjectToCourse.mutate({ courseId: +courseId, subjectId: +subjAddId });
      setSubjAddId(""); // Resetear select
    }
  };

  const handleDetachSubjectsFromCourse = () => {
    if (courseId && subjDelIds.length > 0) {
      detachSubjectsFromCourse.mutate({ courseId: +courseId, subjectIds: subjDelIds });
      setSubjDelIds([]); // Resetear checklist
    }
  };

  /* ───── VÍNCULO Tema ↔ Asignatura ───── */
  const [linkSubjId, setLinkSubjId] = useState("");
  const [themeAddId, setThemeAddId] = useState("");
  const [themeDelIds, setThemeDelIds] = useState<number[]>([]);

  const { data: subjThemes = [], isLoading: loadingSubjThemes } = useThemes(+linkSubjId);

  const themesToAdd = useMemo(
    () => allThemes.filter(t => !subjThemes.some(st => st.id === t.id)),
    [allThemes, subjThemes]
  );

  const handleAddThemeToSubject = () => {
    if (linkSubjId && themeAddId) {
      addThemeToSubject.mutate({ subjectId: +linkSubjId, themeId: +themeAddId });
      setThemeAddId("");
    }
  };

  const handleDetachThemesFromSubject = () => {
    if (linkSubjId && themeDelIds.length > 0) {
      detachThemesFromSubject.mutate({ subjectId: +linkSubjId, themeIds: themeDelIds });
      setThemeDelIds([]);
    }
  };


  return (
    <section id="p2" className={`${styles.container} ${styles.gridWide}`}>
      {/* Curso ↔ Asignatura */}
      <AdminCard title="Asignatura ↔ Curso">
        <div className={styles.vForm}>
          <SelectField id="cselLink" label="Curso" value={courseId}
            options={courseOpts}
            onChange={v => { setCourseId(String(v)); setSubjAddId(""); setSubjDelIds([]); }} />

          <SelectField id="saddLink" label="Añadir asignatura" value={subjAddId}
            options={courseId ? subjToAdd.map(s => ({ id: s.id, label: s.name ?? "Sin nombre" })) : []}
            onChange={v => setSubjAddId(String(v))} />

          <div className={styles.actions}>
            <button disabled={!courseId || !subjAddId || addSubjectToCourse.isPending}
              onClick={handleAddSubjectToCourse}>
              {addSubjectToCourse.isPending ? <Spinner size={16} /> : "Añadir"}
            </button>
          </div>

          <hr className={styles.divider} />

          <MultiCheckList
            title="Asignaturas del curso"
            value={subjDelIds}
            options={subjToDel.map((s: AdminDataItem) => ({ id: s.id, label: s.name }))}
            onChange={ids => setSubjDelIds(ids)}
          />

          <div className={styles.actions}>
            <button className={styles.remove}
              disabled={!courseId || !subjDelIds.length || detachSubjectsFromCourse.isPending}
              onClick={handleDetachSubjectsFromCourse}>
              {detachSubjectsFromCourse.isPending ? <Spinner size={16} /> : "Quitar seleccionadas"}
            </button>
          </div>
        </div>
      </AdminCard>

      {/* Tema ↔ Asignatura */}
      <AdminCard title="Tema ↔ Asignatura">
        <div className={styles.vForm}>
          <SelectField id="subjForThemeLink" label="Asignatura"
            value={linkSubjId} onChange={v => { setLinkSubjId(String(v)); setThemeAddId(""); setThemeDelIds([]); }}
            options={subjectOpts} />

          {loadingSubjThemes
            ? <Spinner size={24} />
            : (
              <SelectField id="themeAddLink" label="Tema"
                value={themeAddId} onChange={v => setThemeAddId(String(v))}
                options={themesToAdd.map(t => ({ id: t.id, label: t.title ?? "Sin título" }))} />
            )}

          <div className={styles.actions}>
            <button disabled={!linkSubjId || !themeAddId || addThemeToSubject.isPending}
              onClick={handleAddThemeToSubject}>
              {addThemeToSubject.isPending ? <Spinner size={16} /> : "Añadir"}
            </button>
          </div>

          <hr className={styles.divider} />

          <MultiCheckList
            title="Temas de la asignatura"
            value={themeDelIds}
            options={subjThemes.map(t => ({ id: t.id, label: t.title }))}
            onChange={ids => setThemeDelIds(ids)}
          />

          <div className={styles.actions}>
            <button className={styles.remove}
              disabled={!linkSubjId || !themeDelIds.length || detachThemesFromSubject.isPending}
              onClick={handleDetachThemesFromSubject}>
              {detachThemesFromSubject.isPending ? <Spinner size={16} /> : "Quitar seleccionados"}
            </button>
          </div>
        </div>
      </AdminCard>
    </section>
  );
}
