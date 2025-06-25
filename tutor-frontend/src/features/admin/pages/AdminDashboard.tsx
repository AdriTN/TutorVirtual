/* --------------------------------------------------------------------
   AdminDashboard.tsx – panel CRUD para cursos / asignaturas / temas
--------------------------------------------------------------------- */
import {
  useState,
  useMemo,
  useCallback,
} from "react";
import { useQueryClient, useMutation } from "@tanstack/react-query";

import NavBar   from "@components/organisms/NavBar/NavBar";
import Footer   from "@components/organisms/Footer/Footer";
import Spinner  from "@components/atoms/Spinner/Spinner";

import {
  AdminCard,
  CrudModal,
  SelectField,
  TabButton,
  Toast,
} from "@features/admin/components";

import { useCourses   } from "@features/explore/hooks/useCourses";
import { useSubjects  } from "../hooks/useSubjects";
import { useThemes    } from "../hooks/useThemes";

import {
  adminCreateCourse,
  adminCreateSubject,
  adminCreateTheme,
  adminAddSubjectToCourse,
  adminRemoveSubjectFromCourse,
  adminAddThemeToSubject,
} from "@services/api/endpoints";

import styles from "./AdminDashboard.module.css";

/* util ---------------------------------------------------------------- */
const toInt = (v: string) => Number.parseInt(v, 10);
type ToastState =
  | { msg: string; varnt: "success" | "error" | "info" }
  | null;

/* ==================================================================== */
export default function AdminDashboard() {
  const qc = useQueryClient();

  /* ──────────────── Datos base ──────────────── */
  const { data: courses = [],  isLoading: loadingCourses  } = useCourses();
  const { data: subjects = [], isLoading: loadingSubjects } = useSubjects();

  const courseOpts  = useMemo(
    () => courses.map(c => ({ id: c.id, label: c.title })), [courses],
  );
  const subjectOpts = useMemo(
    () => subjects.map(s => ({ id: s.id, label: s.name })), [subjects],
  );

  /* ──────────────── Estado UI global ──────────────── */
  const [tab,   setTab]   = useState<"catalog" | "links" | "users">("catalog");
  const [toast, setToast] = useState<ToastState>(null);

  /* ── control de modales ── */
  const [showCourse,  setShowCourse]  = useState(false);
  const [showSubject, setShowSubject] = useState(false);
  const [showTheme,   setShowTheme]   = useState(false);

  /* modals: onClose (evita desmontaje) */
  const closeCourseModal  = useCallback(() => setShowCourse(false),  []);
  const closeSubjectModal = useCallback(() => setShowSubject(false), []);
  const closeThemeModal   = useCallback(() => setShowTheme(false),   []);

  /* ──────────────── Formularios modales ──────────────── */
  const [cTitle, setCTitle] = useState(""); const [cDesc, setCDesc] = useState("");
  const [sName,  setSName]  = useState(""); const [sDesc, setSDesc] = useState("");
  const [tSubj,  setTSubj]  = useState(""); const [tTitle,setTTitle] = useState("");
  const [tDesc,  setTDesc]  = useState("");

  /* ──────────────── Mutaciones catálogo ──────────────── */
  const createCourse = useMutation({
    mutationFn: () => adminCreateCourse(cTitle, cDesc),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["courses"] });
      setCTitle(""); setCDesc(""); closeCourseModal();
      setToast({ msg: "Curso creado", varnt: "success" });
    },
    onError: () => setToast({ msg: "Error al crear curso", varnt: "error" }),
  });

  const createSubject = useMutation({
    mutationFn: () => adminCreateSubject(sName, sDesc),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["subjects"] });
      setSName(""); setSDesc(""); closeSubjectModal();
      setToast({ msg: "Asignatura creada", varnt: "success" });
    },
    onError: () => setToast({ msg: "Error al crear asignatura", varnt: "error" }),
  });

  const createTheme = useMutation({
    mutationFn: () => adminCreateTheme(tTitle, tDesc, toInt(tSubj)),
    onSuccess: () => {
      if (tSubj) qc.invalidateQueries({ queryKey: ["themes", tSubj] });
      setTTitle(""); setTDesc(""); setTSubj(""); closeThemeModal();
      setToast({ msg: "Tema creado", varnt: "success" });
    },
    onError: () => setToast({ msg: "Error al crear tema", varnt: "error" }),
  });

  /* ──────────────── Vínculos curso ↔ asignatura ──────────────── */
  const [courseId, setCourseId]   = useState("");
  const [subjAddId, setSubjAddId] = useState("");
  const [subjDelId, setSubjDelId] = useState("");

  const courseSel   = courses.find(c => c.id === toInt(courseId));
  const inCourse    = courseSel?.subjects ?? [];

  const subjToAdd   = subjects.filter(s => !inCourse.some(i => i.id === s.id));
  const subjToDel   = inCourse;

  const addSubj = useMutation({
    mutationFn: () => adminAddSubjectToCourse(toInt(courseId), toInt(subjAddId)),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["courses"] });
      setSubjAddId("");
      setToast({ msg: "Asignatura añadida", varnt: "success" });
    },
    onError: () => setToast({ msg: "Error al añadir asignatura", varnt: "error" }),
  });

  const removeSubj = useMutation({
    mutationFn: () => adminRemoveSubjectFromCourse(toInt(courseId), toInt(subjDelId)),
    onMutate: () => {
      if (!window.confirm("¿Quitar la asignatura del curso?")) throw new Error("cancelado");
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["courses"] });
      setSubjDelId("");
      setToast({ msg: "Asignatura desvinculada", varnt: "info" });
    },
    onError: (err) => {
      if ((err as Error).message !== "cancelado")
        setToast({ msg: "Error al desvincular asignatura", varnt: "error" });
    },
  });

  /* ──────────────── Temas ↔ asignatura ──────────────── */
  const [linkSubjId, setLinkSubjId] = useState("");
  const [themeId,    setThemeId]    = useState("");
  const { data: themes = [], isLoading: loadingThemes } = useThemes(toInt(linkSubjId));

  const addTheme = useMutation({
    mutationFn: () => adminAddThemeToSubject(toInt(linkSubjId), toInt(themeId)),
    onSuccess: () => {
      setLinkSubjId(""); setThemeId("");
      setToast({ msg: "Tema vinculado", varnt: "success" });
    },
    onError: () => setToast({ msg: "Error al vincular tema", varnt: "error" }),
  });

  /* ──────────────── Loaders ──────────────── */
  if (loadingCourses || loadingSubjects) {
    return (
      <div className={styles.center}>
        <Spinner size={40} />
      </div>
    );
  }

  /* ─────────────────── Render ─────────────────── */
  return (
    <div className={styles.page}>
      <NavBar />

      <main className={styles.main}>
        {/* ---------- Tabs ---------- */}
        <div className={styles.tabs} role="tablist">
          <TabButton id="tab-cat" controls="panel-cat"
                     active={tab==="catalog"} onClick={()=>setTab("catalog")}
                     label="Catálogo"/>
          <TabButton id="tab-link" controls="panel-link"
                     active={tab==="links"}   onClick={()=>setTab("links")}
                     label="Vínculos"/>
          <TabButton id="tab-user" controls="panel-user"
                     active={tab==="users"}   onClick={()=>setTab("users")}
                     label="Usuarios"/>
        </div>

        {/* ---------- Catálogo ---------- */}
        {tab==="catalog" && (
          <section id="panel-cat" role="tabpanel" aria-labelledby="tab-cat"
                   className={`${styles.container} ${styles.grid}`}>
            <AdminCard title={`Cursos (${courses.length})`}>
              <button onClick={()=>setShowCourse(true)}>Nuevo curso</button>
            </AdminCard>
            <AdminCard title={`Asignaturas (${subjects.length})`}>
              <button onClick={()=>setShowSubject(true)}>Nueva asignatura</button>
            </AdminCard>
            <AdminCard title="Temas (global)">
              <button onClick={()=>setShowTheme(true)}>Nuevo tema</button>
            </AdminCard>
          </section>
        )}

        {/* ---------- Vínculos ---------- */}
        {tab==="links" && (
          <section id="panel-link" role="tabpanel" aria-labelledby="tab-link"
                   className={`${styles.container} ${styles.gridWide}`}>
            {/* Asignatura → Curso */}
            <AdminCard title="Asignatura → Curso">
              <div className={styles.vForm}>
                <SelectField id="selCourse" label="Curso"
                  value={courseId} options={courseOpts}
                  onChange={(v)=>{ setCourseId(v); setSubjAddId(""); setSubjDelId(""); }}/>

                <SelectField id="selSubjAdd" label="Añadir asignatura"
                  value={subjAddId}
                  options={!courseId ? [] : subjToAdd.map(s=>({id:s.id,label:s.name}))}
                  onChange={setSubjAddId}/>

                <button disabled={!courseId||!subjAddId||addSubj.isPending}
                        onClick={()=>addSubj.mutate()}>
                  {addSubj.isPending ? <Spinner size={16}/> : "Añadir"}
                </button>

                <hr className={styles.divider}/>

                <SelectField id="selSubjDel" label="Quitar asignatura"
                  value={subjDelId}
                  options={!courseId ? [] : subjToDel.map(s=>({id:s.id,label:s.name}))}
                  onChange={setSubjDelId}/>

                <button className={styles.remove}
                        disabled={!courseId||!subjDelId||removeSubj.isPending}
                        onClick={()=>removeSubj.mutate()}>
                  {removeSubj.isPending ? <Spinner size={16}/> : "Quitar"}
                </button>
              </div>
            </AdminCard>

            {/* Tema → Asignatura */}
            <AdminCard title="Tema → Asignatura">
              <div className={styles.vForm}>
                <SelectField id="selSubjTheme" label="Asignatura"
                  value={linkSubjId} onChange={setLinkSubjId}
                  options={subjectOpts}/>

                {loadingThemes ? (
                  <Spinner size={24}/>
                ) : (
                  <SelectField id="selTheme" label="Tema"
                    value={themeId} onChange={setThemeId}
                    options={themes.map(t=>({id:t.id,label:t.title}))}/>
                )}

                <button disabled={!linkSubjId||!themeId||addTheme.isPending}
                        onClick={()=>addTheme.mutate()}>
                  {addTheme.isPending ? <Spinner size={16}/> : "Añadir"}
                </button>
              </div>
            </AdminCard>
          </section>
        )}

        {/* ---------- Usuarios (placeholder) ---------- */}
        {tab==="users" && (
          <section id="panel-user" role="tabpanel" aria-labelledby="tab-user"
                   className={styles.container}>
            <p style={{marginTop:"2rem"}}>Aquí podrás gestionar los usuarios (pendiente).</p>
          </section>
        )}

        {/* ---------- Modales ---------- */}
        <CrudModal open={showCourse}  title="Nuevo curso"      onClose={closeCourseModal}>
          <input    placeholder="Título"       value={cTitle} onChange={e=>setCTitle(e.target.value)}/>
          <textarea placeholder="Descripción"  value={cDesc}  onChange={e=>setCDesc(e.target.value)}/>
          <div className={styles.actions}>
            <button onClick={closeCourseModal}>Cancelar</button>
            <button disabled={!cTitle.trim()||createCourse.isPending}
                    onClick={()=>createCourse.mutate()}>
              {createCourse.isPending ? <Spinner size={16}/> : "Guardar"}
            </button>
          </div>
        </CrudModal>

        <CrudModal open={showSubject} title="Nueva asignatura" onClose={closeSubjectModal}>
          <input    placeholder="Nombre"        value={sName} onChange={e=>setSName(e.target.value)}/>
          <textarea placeholder="Descripción"   value={sDesc} onChange={e=>setSDesc(e.target.value)}/>
          <div className={styles.actions}>
            <button onClick={closeSubjectModal}>Cancelar</button>
            <button disabled={!sName.trim()||createSubject.isPending}
                    onClick={()=>createSubject.mutate()}>
              {createSubject.isPending ? <Spinner size={16}/> : "Guardar"}
            </button>
          </div>
        </CrudModal>

        <CrudModal open={showTheme}   title="Nuevo tema"       onClose={closeThemeModal}>
          <SelectField id="selSubjModal" label="Asignatura"
            value={tSubj} onChange={setTSubj} options={subjectOpts}/>
          <input    placeholder="Título"       value={tTitle} onChange={e=>setTTitle(e.target.value)}/>
          <textarea placeholder="Descripción"  value={tDesc}  onChange={e=>setTDesc(e.target.value)}/>
          <div className={styles.actions}>
            <button onClick={closeThemeModal}>Cancelar</button>
            <button disabled={!tSubj||!tTitle.trim()||createTheme.isPending}
                    onClick={()=>createTheme.mutate()}>
              {createTheme.isPending ? <Spinner size={16}/> : "Guardar"}
            </button>
          </div>
        </CrudModal>

        {/* ---------- Toast ---------- */}
        {toast && <Toast message={toast.msg} variant={toast.varnt}/>}
      </main>

      <Footer />
    </div>
  );
}
