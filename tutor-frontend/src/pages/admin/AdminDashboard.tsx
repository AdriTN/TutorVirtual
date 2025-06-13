import { useState, useMemo } from "react";
import { useQueryClient, useMutation } from "@tanstack/react-query";

import { useCourses }  from "../../hooks/useCourses";
import { useSubjects } from "../../hooks/useSubjects";
import { useThemes }   from "../../hooks/useThemes";

import {
  adminCreateCourse, adminCreateSubject, adminCreateTheme,
  adminAddSubjectToCourse, adminRemoveSubjectFromCourse, adminAddThemeToSubject,
  Course, Subject, Theme
} from "../../utils/enrollment";

import NavBar  from "../utils/NavBar/NavBar";
import Footer  from "../utils/Footer/Footer";

import CrudModal      from "../../components/admin/crudmodal/CrudModal";
import { AdminCard }  from "../../components/admin/card/AdminCard";
import { SelectField } from "../../components/admin/field/SelectField";
import { TabButton }  from "../../components/admin/tabbutton/TabButton";
import { Toast }      from "../../components/admin/toast/Toast";

import styles from "./AdminDashboard.module.css";
import { Spinner } from "../../components/spinner/Spinner";

const toInt = (v: string) => Number.parseInt(v, 10);

type ToastState = { msg: string; varnt: "success"|"error"|"info" } | null;

export default function AdminDashboard() {
  const qc = useQueryClient();

  /* ---------- datos base ---------- */
  const coursesQ  = useCourses();                     // AxiosResponse<Course[]>
  const subjectsQ = useSubjects();                    // AxiosResponse<Subject[]>
  const courseList:  Course[]  = coursesQ.data?.data  ?? [];
  const subjectList: Subject[] = subjectsQ.data?.data ?? [];

  /* ---------- UI state ---------- */
  const [tab, setTab] = useState<"catalog"|"links"|"users">("catalog");
  const [toast, setToast] = useState<ToastState>(null);

  /* ---------- catálogos (modals) ---------- */
  const [showCourse,setShowCourse]   = useState(false);
  const [showSubject,setShowSubject] = useState(false);
  const [showTheme,setShowTheme]     = useState(false);

  const [cTitle,setCTitle] = useState(""); const [cDesc,setCDesc] = useState("");
  const [sName,setSName]   = useState(""); const [sDesc,setSDesc] = useState("");
  const [tTitle,setTTitle] = useState("");const [tDesc,setTDesc]  = useState("");const [tSubj,setTSubj]=useState("");

  /* ---------- mutaciones catálogo ---------- */
  const createCourse = useMutation({
    mutationFn: () => adminCreateCourse(cTitle, cDesc),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["courses"] });
      setCTitle(""); setCDesc(""); setShowCourse(false);
      setToast({ msg: "Curso creado", varnt: "success" });
    },
    onError: () => setToast({ msg: "Error al crear curso", varnt: "error" })
  });

  const createSubject = useMutation({
    mutationFn: () => adminCreateSubject(sName, sDesc),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["subjects"] });
      setSName(""); setSDesc(""); setShowSubject(false);
      setToast({ msg: "Asignatura creada", varnt: "success" });
    },
    onError: () => setToast({ msg: "Error al crear asignatura", varnt: "error" })
  });

  const createTheme = useMutation({
    mutationFn: () => adminCreateTheme(tTitle, tDesc, toInt(tSubj)),
    onSuccess: () => {
      if (tSubj) qc.invalidateQueries({ queryKey: ["themes", tSubj] });
      setTTitle(""); setTDesc(""); setTSubj(""); setShowTheme(false);
      setToast({ msg: "Tema creado", varnt: "success" });
    },
    onError: () => setToast({ msg: "Error al crear tema", varnt: "error" })
  });

  /* ---------- links ---------- */
  const [courseId,setCourseId]   = useState("");
  const [subjectId,setSubjectId] = useState("");
  const [linkSubjId,setLinkSubjId] = useState("");
  const [themeId,setThemeId]     = useState("");

  const subjectsByCourse: Subject[] = useMemo(() => {
    if (!courseId) return subjectList;
    const course = courseList.find((c) => c.id === toInt(courseId));
    return course ? course.subjects : [];
  }, [courseId, courseList, subjectList]);

  const themesQ = useThemes(linkSubjId);
  const themeList: Theme[] = themesQ.data?.data ?? [];

  const addSubj = useMutation({
    mutationFn: () => adminAddSubjectToCourse(toInt(courseId), toInt(subjectId)),
    onSuccess: () => {
      setCourseId(""); setSubjectId("");
      setToast({msg:"Asignatura añadida",varnt:"success"});
    },
    onError: () => setToast({msg:"Error al añadir asignatura",varnt:"error"})
  });

  const removeSubj = useMutation({
    mutationFn: () => adminRemoveSubjectFromCourse(toInt(courseId), toInt(subjectId)),
    onMutate: async () => {
      if (!window.confirm("¿Quitar la asignatura del curso?")) throw new Error("cancelado");
    },
    onSuccess: () => {
      setCourseId(""); setSubjectId("");
      setToast({msg:"Asignatura desvinculada",varnt:"info"});
    },
    onError: (err) => {
      if ((err as Error).message !== "cancelado")
        setToast({msg:"Error al desvincular asignatura",varnt:"error"});
    }
  });

  const addTheme = useMutation({
    mutationFn: () => adminAddThemeToSubject(toInt(linkSubjId), toInt(themeId)),
    onSuccess: () => { setLinkSubjId(""); setThemeId(""); setToast({msg:"Tema vinculado",varnt:"success"}); },
    onError: () => setToast({msg:"Error al vincular tema",varnt:"error"})
  });

  /* ---------- loaders globales ---------- */
  if (coursesQ.isLoading || subjectsQ.isLoading)
    return <div style={{display:"flex",justifyContent:"center",marginTop:"4rem"}}><Spinner size={40}/></div>;

  if (coursesQ.isError || subjectsQ.isError)
    return <Toast message="Error al cargar datos" variant="error" />;

  /* ---------- render ---------- */
  return (
    <>
      <div className={styles.page}>
        <NavBar />

        <main className={styles.main}>

          {/* Tabs */}
          <div className={styles.tabs} role="tablist">
            <TabButton id="tab-cat"  controls="panel-cat"  active={tab==="catalog"} onClick={()=>setTab("catalog")}>Catálogo</TabButton>
            <TabButton id="tab-link" controls="panel-link" active={tab==="links"}   onClick={()=>setTab("links")}>Vínculos</TabButton>
            <TabButton id="tab-user" controls="panel-user" active={tab==="users"}   onClick={()=>setTab("users")}>Usuarios</TabButton>
          </div>

          {/* ---------- Catálogo ---------- */}
          {tab==="catalog" && (
            <section id="panel-cat" role="tabpanel" aria-labelledby="tab-cat"
                    className={`${styles.container} ${styles.grid}`}>
              <AdminCard title={`Cursos (${courseList.length})`}>
                <button onClick={()=>setShowCourse(true)}>Nuevo curso</button>
              </AdminCard>
              <AdminCard title={`Asignaturas (${subjectList.length})`}>
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

              <AdminCard title="Asignatura → Curso">
                <div className={styles.vForm}>
                  <SelectField id="selCourse" label="Curso" value={courseId}
                    onChange={v=>{setCourseId(v); setSubjectId("");}}
                    options={courseList.map(c=>({id:c.id,label:c.title}))}/>

                  <SelectField id="selSubj" label="Asignatura" value={subjectId}
                    onChange={setSubjectId}
                    options={subjectsByCourse.map(s=>({id:s.id,label:s.name}))}/>

                  <div className={styles.actions}>
                    <button disabled={!courseId||!subjectId||addSubj.isPending}
                            onClick={()=>addSubj.mutate()}>
                      {addSubj.isPending ? <Spinner size={16}/> : "Añadir"}
                    </button>

                    <button className={styles.remove}
                            disabled={!courseId||!subjectId||removeSubj.isPending}
                            onClick={()=>removeSubj.mutate()}>
                      {removeSubj.isPending ? <Spinner size={16}/> : "Quitar"}
                    </button>
                  </div>
                </div>
              </AdminCard>

              <AdminCard title="Tema → Asignatura">
                <div className={styles.vForm}>
                  <SelectField id="selSubjTheme" label="Asignatura" value={linkSubjId}
                    onChange={setLinkSubjId}
                    options={subjectList.map(s=>({id:s.id,label:s.name}))}/>

                  {themesQ.isLoading ? (
                    <Spinner size={24}/>
                  ) : (
                    <SelectField id="selTheme" label="Tema" value={themeId}
                      onChange={setThemeId}
                      options={themeList.map(t=>({id:t.id,label:t.title}))}/>
                  )}

                  <button disabled={!linkSubjId||!themeId||addTheme.isPending}
                          onClick={()=>addTheme.mutate()}>
                    {addTheme.isPending ? <Spinner size={16}/> : "Añadir"}
                  </button>
                </div>
              </AdminCard>
            </section>
          )}

          {/* ---------- Usuarios placeholder ---------- */}
          {tab==="users" && (
            <section id="panel-user" role="tabpanel" aria-labelledby="tab-user"
                    className={styles.container}>
              <p style={{marginTop:"2rem"}}>Aquí podrás gestionar los usuarios (pendiente).</p>
            </section>
          )}

          {/* ---------- Modales ---------- */}
          <CrudModal open={showCourse} title="Nuevo curso" onClose={()=>setShowCourse(false)}>
            <input placeholder="Título" value={cTitle} onChange={e=>setCTitle(e.target.value)}/>
            <textarea placeholder="Descripción" value={cDesc} onChange={e=>setCDesc(e.target.value)}/>
            <div className={styles.actions}>
              <button onClick={()=>setShowCourse(false)}>Cancelar</button>
              <button disabled={!cTitle.trim()||createCourse.isPending}
                      onClick={()=>createCourse.mutate()}>
                {createCourse.isPending ? <Spinner size={16}/> : "Guardar"}
              </button>
            </div>
          </CrudModal>

          <CrudModal open={showSubject} title="Nueva asignatura" onClose={()=>setShowSubject(false)}>
            <input placeholder="Nombre" value={sName} onChange={e=>setSName(e.target.value)}/>
            <textarea placeholder="Descripción" value={sDesc} onChange={e=>setSDesc(e.target.value)}/>
            <div className={styles.actions}>
              <button onClick={()=>setShowSubject(false)}>Cancelar</button>
              <button disabled={!sName.trim()||createSubject.isPending}
                      onClick={()=>createSubject.mutate()}>
                {createSubject.isPending ? <Spinner size={16}/> : "Guardar"}
              </button>
            </div>
          </CrudModal>

          <CrudModal open={showTheme} title="Nuevo tema" onClose={()=>setShowTheme(false)}>
            <SelectField id="selSubjModal" label="Asignatura" value={tSubj}
              onChange={setTSubj}
              options={subjectList.map(s=>({id:s.id,label:s.name}))}/>
            <input placeholder="Título" value={tTitle} onChange={e=>setTTitle(e.target.value)}/>
            <textarea placeholder="Descripción" value={tDesc} onChange={e=>setTDesc(e.target.value)}/>
            <div className={styles.actions}>
              <button onClick={()=>setShowTheme(false)}>Cancelar</button>
              <button disabled={!tSubj||!tTitle.trim()||createTheme.isPending}
                      onClick={()=>createTheme.mutate()}>
                {createTheme.isPending ? <Spinner size={16}/> : "Guardar"}
              </button>
            </div>
          </CrudModal>

          {/* ---------- Toast global ---------- */}
          {toast && <Toast message={toast.msg} variant={toast.varnt}/>}
        </main>
        <Footer />
      </div>
    </>
  );
}