/* ------------------------------------------------------------------
   AdminDashboard – Panel CRUD (Cursos · Asignaturas · Temas)
-------------------------------------------------------------------*/
import { useMemo, useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";

import NavBar  from "@components/organisms/NavBar/NavBar";
import Footer  from "@components/organisms/Footer/Footer";
import Spinner from "@components/atoms/Spinner/Spinner";

import {
  AdminCard,
  ConfirmDialog,
  CrudModal,
  EntityTable,
  SelectField,
  TabButton,
  Toast,
  MultiCheckList,
} from "@features/admin/components";

import { useCourses }          from "@features/explore/hooks/useCourses";
import { useSubjects }         from "../hooks/useSubjects";
import { useThemes, useAllThemes } from "../hooks/useThemes";

/* ───── Endpoints ───── */
import {
  /* Courses */
  adminCreateCourse,  adminUpdateCourse,  adminDeleteCourse,
  adminAddSubjectToCourse, adminDetachSubjectsFromCourse,
  /* Subjects */
  adminCreateSubject, adminUpdateSubject, adminDeleteSubject,
  adminAddThemeToSubject,  adminDetachThemesFromSubject,
  /* Themes   */
  adminCreateTheme,   adminUpdateTheme,   adminDeleteTheme,
} from "@services/api/endpoints";

import styles from "./AdminDashboard.module.css";

/* helpers ---------------------------------------------------------- */
type ToastState =
  | { msg: string; varnt: "success" | "error" | "info" }
  | null;

/* ================================================================== */
export default function AdminDashboard() {
  const qc = useQueryClient();

  /* ───── datos base ───── */
  const { data: courses   = [], isLoading: loadingCourses  } = useCourses();
  const { data: subjects  = [], isLoading: loadingSubjects } = useSubjects();
  const { data: allThemes = [], isLoading: loadingThemes   } = useAllThemes();

  /* ───── opciones & mapas ───── */
  const subjMap     = useMemo(() => new Map(subjects.map(s => [s.id, s.name])), [subjects]);
  const courseOpts  = useMemo(() => courses .map(c => ({ id: c.id, label: c.title })), [courses ]);
  const subjectOpts = useMemo(() => subjects.map(s => ({ id: s.id, label: s.name  })), [subjects]);

  const themeRows = useMemo(
    () => allThemes.map(t => ({
      id: t.id, title: t.title,
      description: t.description ?? "—",
      subject: subjMap.get(t.subject_id) ?? "—",
      subject_id: t.subject_id,
    })),
    [allThemes, subjMap],
  );

  /* ───── estado UI global ───── */
  const [tab,   setTab]   = useState<"catalog" | "links" | "manage">("catalog");
  const [toast, setToast] = useState<ToastState>(null);
  const ok   = (msg:string)=>setToast({msg, varnt:"success"});
  const fail = (msg:string)=>setToast({msg, varnt:"error"  });

  /* ================================================================
     1 · ALTAS
  ================================================================ */
  const [showCourse,  setShowCourse ] = useState(false);
  const [showSubject, setShowSubject] = useState(false);
  const [showTheme,   setShowTheme  ] = useState(false);

  const [cTitle, setCTitle] = useState("");  const [cDesc,  setCDesc ] = useState("");
  const [sName,  setSName ] = useState("");  const [sDesc,  setSDesc ] = useState("");
  const [tSubj,  setTSubj ] = useState("");  const [tTitle, setTTitle] = useState("");
  const [tDesc,  setTDesc ] = useState("");

  const createCourse = useMutation({
    mutationFn: () => adminCreateCourse(cTitle, cDesc),
    onSuccess: async () => {
      await qc.invalidateQueries({ queryKey: ["courses/all"], exact: true });
      setShowCourse(false); setCTitle(""); setCDesc("");
      ok("Curso creado");
    },
    onError  : () => fail("Error al crear curso"),
  });

  const createSubject = useMutation({
    mutationFn: () => adminCreateSubject(sName, sDesc),
    onSuccess: async () => {
      await qc.invalidateQueries({ queryKey: ["subjects"], exact: true });
      setShowSubject(false); setSName(""); setSDesc("");
      ok("Asignatura creada");
    },
    onError  : () => fail("Error al crear asignatura"),
  });

  const createTheme = useMutation({
    mutationFn: () => adminCreateTheme(tTitle, tDesc, +tSubj),
    onSuccess: async () => {
      await qc.invalidateQueries({ queryKey: ["all-themes"], exact: true });
      await qc.invalidateQueries({ queryKey: ["themes"],     exact: true });
      setShowTheme(false); setTSubj(""); setTTitle(""); setTDesc("");
      ok("Tema creado");
    },
    onError  : () => fail("Error al crear tema"),
  });

  /* ================================================================
     2 · EDICIÓN
  ================================================================ */
  type Kind = "course" | "subject" | "theme";
  const [editKind, setEditKind] = useState<Kind | null>(null);
  const [editItem, setEditItem] = useState<any>(null);

  const startEdit = (kind:Kind,item:any) => {
    setEditKind(kind); setEditItem(item);
    if(kind==="course"){ setCTitle(item.title); setCDesc(item.description??""); }
    if(kind==="subject"){ setSName(item.name);  setSDesc(item.description??""); }
    if(kind==="theme"){
      setTTitle(item.title); setTDesc(item.description??"");
      setTSubj(String(item.subject_id));
    }
  };
  const closeEdit = () => { setEditKind(null); setEditItem(null); };

  const updateCourse = useMutation({
    mutationFn: () =>
      adminUpdateCourse(editItem.id, { title: cTitle, description: cDesc }),
    onSuccess: () => {
      qc.setQueryData(['courses/all'], (old: any[] = []) =>
        old.map(c =>
          c.id === editItem.id ? { ...c, title: cTitle, description: cDesc } : c
        )
      );
      qc.invalidateQueries({ queryKey: ['courses/all'], exact: true });
      ok('Curso actualizado');
      closeEdit();
    },
  });

  const updateSubject = useMutation({
    mutationFn: () =>
      adminUpdateSubject(editItem.id,{name:sName,description:sDesc}),
    onSuccess: async () => {
      qc.setQueryData(["subjects"], (old: any[] = []) =>
        old.map((s: any) =>
          s.id === editItem.id ? { ...s, name: sName, description: sDesc } : s
        )
      );
      await qc.invalidateQueries({ queryKey: ["subjects"], exact: true });
      ok("Asignatura actualizada"); closeEdit();
    },
    onError  : () => fail("Error al actualizar asignatura"),
  });

  const updateTheme = useMutation({
    mutationFn: () =>
      adminUpdateTheme(editItem.id,{
        name:tTitle, description:tDesc, subject_id:+tSubj,
      }),
    onSuccess: async () => {
      qc.setQueryData(["all-themes"], (old: any[] = []) =>
        old.map((t: any) =>
          t.id === editItem.id
            ? { ...t, title: tTitle, description: tDesc, subject_id: +tSubj }
            : t
        )
      );
      await qc.invalidateQueries({ queryKey: ["all-themes"], exact: true });
      await qc.invalidateQueries({ queryKey: ["themes"],     exact: true });
      ok("Tema actualizado"); closeEdit();
    },
    onError  : () => fail("Error al actualizar tema"),
  });

  /* ================================================================
     3 · BORRADO
  ================================================================ */
  const [confirm,setConfirm] = useState<{kind:Kind,id:number,label:string}|null>(null);
  const delCourse = useMutation({
    mutationFn: adminDeleteCourse,
    onSuccess: (_data, id: number) => {
      qc.setQueryData(['courses/all'], (old: any[] = []) =>
        old.filter(c => c.id !== id)
      );
      qc.invalidateQueries({ queryKey: ['courses/all'], exact: true });
      ok('Curso eliminado');
    },
  });
  const delSubject = useMutation({
    mutationFn: adminDeleteSubject,
    onSuccess: async (_data, id: number) => {
      qc.setQueryData(["subjects"], (old: any[] = []) =>
        old.filter((s: any)=>s.id !== id)
      );
      await qc.invalidateQueries({ queryKey: ["subjects"], exact: true });
      ok("Asignatura eliminada");
    },
    onError  : ()=> fail("Error al eliminar asignatura"),
  });
  const delTheme = useMutation({
    mutationFn: adminDeleteTheme,
    onSuccess: async (_data, id: number) => {
      qc.setQueryData(["all-themes"], (old: any[] = []) =>
        old.filter((t: any)=>t.id !== id)
      );
      await qc.invalidateQueries({ queryKey: ["all-themes"], exact: true });
      ok("Tema eliminado");
    },
    onError  : ()=> fail("Error al eliminar tema"),
  });
  const doDelete = () => {
    if(!confirm) return;
    const {kind,id}=confirm;
    if(kind==="course")  delCourse.mutate(id);
    if(kind==="subject") delSubject.mutate(id);
    if(kind==="theme")   delTheme  .mutate(id);
    setConfirm(null);
  };

  /* ================================================================
     4 · VÍNCULO Curso ↔ Asignatura
  ================================================================ */
  const [courseId,   setCourseId]   = useState("");
  const [subjAddId,  setSubjAddId]  = useState("");
  const [subjDelIds, setSubjDelIds] = useState<number[]>([]);

  const courseSel   = courses.find(c=>c.id===+courseId);
  const inCourse    = courseSel?.subjects ?? [];
  const subjToAdd   = subjects.filter(s=>!inCourse.some(i=>i.id===s.id));
  const subjToDel   = inCourse;

  const addSubj = useMutation({
    mutationFn: () => adminAddSubjectToCourse(+courseId, +subjAddId),
    onSuccess: async () => {
      /* Actualiza localmente para feedback instantáneo */
      qc.setQueryData(["courses/all"], (prev: any[] = []) =>
        prev.map(c =>
          c.id === +courseId
            ? { ...c, subjects: [...c.subjects, subjects.find(s => s.id === +subjAddId)!] }
            : c
        )
      );
      /* Y sincroniza con el servidor */
      await qc.invalidateQueries({ queryKey: ["courses/all"], exact: true });
      setSubjAddId("");
      ok("Asignatura añadida");
    },
    onError: () => fail("Error al añadir asignatura"),
  });
  const detachSubjs = useMutation({
    mutationFn: () => adminDetachSubjectsFromCourse(+courseId, subjDelIds.map(Number)),
    onSuccess: async () => {
      qc.setQueryData(["courses/all"], (prev: any[] = []) =>
        prev.map(c =>
          c.id === +courseId
            ? { ...c, subjects: c.subjects.filter((s: any) => !subjDelIds.includes(Number(s.id))) }
            : c
        )
      );
      await qc.invalidateQueries({ queryKey: ["courses/all"], exact: true });
      setSubjDelIds([]);
      ok("Asignaturas desvinculadas");
    },
    onError: () => fail("Error al desvincular asignaturas"),
  });

  /* ================================================================
     5 · VÍNCULO Tema ↔ Asignatura
  ================================================================ */
  const [linkSubjId,setLinkSubjId] = useState("");
  const [themeId,   setThemeId]    = useState("");
  const [themeIds,  setThemeIds]   = useState<number[]>([]);

  const { data:subjThemes=[], isLoading:loadingSubjThemes } = useThemes(+linkSubjId);

  const themesToAdd = useMemo(
    () =>
      allThemes.filter(
        t => !subjThemes.some(st => st.id === t.id)
      ),
    [allThemes, subjThemes]
  );

  const addTheme = useMutation({
    mutationFn: () => adminAddThemeToSubject(+linkSubjId, +themeId),
    onSuccess: async () => {
      qc.setQueryData(["themes", +linkSubjId], (prev: any[] = []) => [
        ...prev,
        allThemes.find(t => t.id === +themeId)!,
      ]);
      await qc.invalidateQueries({ queryKey: ["themes", +linkSubjId], exact: true });
      await qc.invalidateQueries({ queryKey: ["all-themes"],          exact: true });
      setLinkSubjId("");
      setThemeId("");
      ok("Tema vinculado");
    },
    onError: () => fail("Error al vincular tema"),
  });
  const detachThemes = useMutation({
    mutationFn: () => adminDetachThemesFromSubject(+linkSubjId, themeIds.map(Number)),
    onSuccess: async () => {
      qc.setQueryData(["themes", +linkSubjId], (prev: any[] = []) =>
        prev.filter((t: any) => !themeIds.includes(Number(t.id)))
      );
      await qc.invalidateQueries({ queryKey: ["themes", +linkSubjId], exact: true });
      await qc.invalidateQueries({ queryKey: ["all-themes"],          exact: true });
      setThemeIds([]);
      ok("Temas desvinculados");
    },
    onError: () => fail("Error al desvincular temas"),
  });

  /* loaders */
  if (loadingCourses || loadingSubjects)
    return <div className={styles.center}><Spinner size={40}/></div>;

  /* ================================================================
     RENDER
  ================================================================ */
  return (
    <div className={styles.page}>
      <NavBar />

      <main className={styles.main}>

        {/* Tabs */}
        <div className={styles.tabs} role="tablist">
          <TabButton id="t1" label="Catálogo"  controls="p1"
            active={tab==="catalog"} onClick={()=>setTab("catalog")} />
          <TabButton id="t2" label="Vínculos"   controls="p2"
            active={tab==="links"}   onClick={()=>setTab("links")}   />
          <TabButton id="t3" label="Gestionar" controls="p3"
            active={tab==="manage"}  onClick={()=>setTab("manage")}  />
        </div>

        {/* 1· Catálogo ------------------------------------------------ */}
        {tab==="catalog" && (
          <section id="p1" className={`${styles.container} ${styles.grid}`}>
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

        {/* 2· Vínculos ----------------------------------------------- */}
        {tab==="links" && (
          <section id="p2" className={`${styles.container} ${styles.gridWide}`}>

            {/* Curso ↔ Asignatura */}
            <AdminCard title="Asignatura ↔ Curso">
              <div className={styles.vForm}>
                <SelectField id="csel" label="Curso" value={courseId}
                  options={courseOpts}
                  onChange={v=>{ setCourseId(String(v)); setSubjAddId(""); setSubjDelIds([]);} } />

                <SelectField id="sadd" label="Añadir asignatura" value={subjAddId}
                  options={courseId ? subjToAdd.map(s=>({id:s.id,label:s.name})) : []}
                  onChange={v=>setSubjAddId(String(v))} />

                <div className={styles.actions}>
                  <button disabled={!courseId||!subjAddId||addSubj.isPending}
                          onClick={()=>addSubj.mutate()}>
                    {addSubj.isPending ? <Spinner size={16}/> : "Añadir"}
                  </button>
                </div>

                <hr className={styles.divider}/>

                <MultiCheckList
                  title="Asignaturas del curso"
                  value={subjDelIds}
                  options={subjToDel.map(s=>({id:s.id,label:s.name}))}
                  onChange={ids=>setSubjDelIds(ids)}
                />

                <div className={styles.actions}>
                  <button className={styles.remove}
                          disabled={!courseId||!subjDelIds.length||detachSubjs.isPending}
                          onClick={()=>detachSubjs.mutate()}>
                    {detachSubjs.isPending ? <Spinner size={16}/> : "Quitar seleccionadas"}
                  </button>
                </div>
              </div>
            </AdminCard>

            {/* Tema ↔ Asignatura */}
            <AdminCard title="Tema ↔ Asignatura">
              <div className={styles.vForm}>
                <SelectField id="subjForTheme" label="Asignatura"
                  value={linkSubjId} onChange={v=>setLinkSubjId(String(v))}
                  options={subjectOpts} />

                {loadingSubjThemes
                  ? <Spinner size={24}/>
                  : (
                    <SelectField id="themeAdd" label="Tema"
                      value={themeId} onChange={v=>setThemeId(String(v))}
                      options={themesToAdd.map(t => ({ id: t.id, label: t.title }))} />
                  )}

                <div className={styles.actions}>
                  <button disabled={!linkSubjId||!themeId||addTheme.isPending}
                          onClick={()=>addTheme.mutate()}>
                    {addTheme.isPending ? <Spinner size={16}/> : "Añadir"}
                  </button>
                </div>

                <hr className={styles.divider}/>

                <MultiCheckList
                  title="Temas de la asignatura"
                  value={themeIds}
                  options={subjThemes.map(t=>({id:t.id,label:t.title}))}
                  onChange={ids=>setThemeIds(ids)}
                />

                <div className={styles.actions}>
                  <button className={styles.remove}
                          disabled={!linkSubjId||!themeIds.length||detachThemes.isPending}
                          onClick={()=>detachThemes.mutate()}>
                    {detachThemes.isPending ? <Spinner size={16}/> : "Quitar seleccionados"}
                  </button>
                </div>
              </div>
            </AdminCard>
          </section>
        )}

        {/* 3· Gestión completa --------------------------------------- */}
        {tab==="manage" && (
          <section id="p3" className={`${styles.container} ${styles.managePanel}`}>

            <AdminCard title="Cursos">
              <EntityTable
                items={courses}
                cols={[
                  { key:"title",       label:"Título" },
                  { key:"description", label:"Descripción" },
                ]}
                onEdit={item=>startEdit("course",item)}
                onDelete={item=>setConfirm({kind:"course",id:item.id,label:item.title})}
              />
            </AdminCard>

            <AdminCard title="Asignaturas">
              <EntityTable
                items={subjects}
                cols={[
                  { key:"name",        label:"Nombre" },
                  { key:"description", label:"Descripción" },
                ]}
                onEdit={item=>startEdit("subject",item)}
                onDelete={item=>setConfirm({kind:"subject",id:item.id,label:item.name})}
              />
            </AdminCard>

            <AdminCard title="Temas">
              {loadingThemes
                ? <Spinner size={24}/>
                : (
                  <EntityTable
                    items={themeRows}
                    cols={[
                      { key:"title",       label:"Tema" },
                      { key:"subject",     label:"Asignatura" },
                      { key:"description", label:"Descripción" },
                    ]}
                    onEdit={item=>startEdit("theme",item)}
                    onDelete={item=>setConfirm({kind:"theme",id:item.id,label:item.title})}
                  />
                )}
            </AdminCard>
          </section>
        )}

        {/* Modales ALTAS */}
        <CrudModal open={showCourse} title="Nuevo curso" onClose={()=>setShowCourse(false)}>
          <input
            value={cTitle} onChange={e=>setCTitle(e.target.value)} placeholder="Título"/>
          <textarea
            value={cDesc}  onChange={e=>setCDesc (e.target.value)} placeholder="Descripción"/>
          <div className={styles.actions}>
            <button onClick={()=>setShowCourse(false)}>Cancelar</button>
            <button disabled={!cTitle.trim()||createCourse.isPending}
                    onClick={()=>createCourse.mutate()}>
              {createCourse.isPending?<Spinner size={16}/>:"Guardar"}
            </button>
          </div>
        </CrudModal>

        <CrudModal open={showSubject} title="Nueva asignatura" onClose={()=>setShowSubject(false)}>
          <input
            value={sName} onChange={e=>setSName(e.target.value)} placeholder="Nombre"/>
          <textarea
            value={sDesc} onChange={e=>setSDesc(e.target.value)} placeholder="Descripción"/>
          <div className={styles.actions}>
            <button onClick={()=>setShowSubject(false)}>Cancelar</button>
            <button disabled={!sName.trim()||createSubject.isPending}
                    onClick={()=>createSubject.mutate()}>
              {createSubject.isPending?<Spinner size={16}/>:"Guardar"}
            </button>
          </div>
        </CrudModal>

        <CrudModal open={showTheme} title="Nuevo tema" onClose={()=>setShowTheme(false)}>
          <SelectField id="subj4theme" label="Asignatura"
            value={tSubj} onChange={v=>setTSubj(String(v))} options={subjectOpts}/>
          <input
            value={tTitle} onChange={e=>setTTitle(e.target.value)} placeholder="Título"/>
          <textarea
            value={tDesc}  onChange={e=>setTDesc (e.target.value)} placeholder="Descripción"/>
          <div className={styles.actions}>
            <button onClick={()=>setShowTheme(false)}>Cancelar</button>
            <button disabled={!tSubj||!tTitle.trim()||createTheme.isPending}
                    onClick={()=>createTheme.mutate()}>
              {createTheme.isPending?<Spinner size={16}/>:"Guardar"}
            </button>
          </div>
        </CrudModal>

        {/* Modal EDICIÓN */}
        <CrudModal open={!!editKind} title="Editar" onClose={closeEdit}>
          {editKind==="course" && (
            <>
              <input
                value={cTitle} onChange={e=>setCTitle(e.target.value)} placeholder="Título"/>
              <textarea
                value={cDesc}  onChange={e=>setCDesc (e.target.value)} placeholder="Descripción"/>
              <div className={styles.actions}>
                <button onClick={closeEdit}>Cancelar</button>
                <button disabled={updateCourse.isPending}
                        onClick={()=>updateCourse.mutate()}>
                  {updateCourse.isPending?<Spinner size={16}/>:"Guardar"}
                </button>
              </div>
            </>
          )}

          {editKind==="subject" && (
            <>
              <input
                value={sName} onChange={e=>setSName(e.target.value)} placeholder="Nombre"/>
              <textarea
                value={sDesc} onChange={e=>setSDesc(e.target.value)} placeholder="Descripción"/>
              <div className={styles.actions}>
                <button onClick={closeEdit}>Cancelar</button>
                <button disabled={updateSubject.isPending}
                        onClick={()=>updateSubject.mutate()}>
                  {updateSubject.isPending?<Spinner size={16}/>:"Guardar"}
                </button>
              </div>
            </>
          )}

          {editKind==="theme" && (
            <>
              <SelectField id="editThemeSubj" label="Asignatura"
                value={tSubj} onChange={v=>setTSubj(String(v))} options={subjectOpts}/>
              <input
                value={tTitle} onChange={e=>setTTitle(e.target.value)} placeholder="Título"/>
              <textarea
                value={tDesc}  onChange={e=>setTDesc (e.target.value)} placeholder="Descripción"/>
              <div className={styles.actions}>
                <button onClick={closeEdit}>Cancelar</button>
                <button disabled={updateTheme.isPending}
                        onClick={()=>updateTheme.mutate()}>
                  {updateTheme.isPending?<Spinner size={16}/>:"Guardar"}
                </button>
              </div>
            </>
          )}
        </CrudModal>

        {/* Confirmar borrado */}
        <ConfirmDialog
          open={!!confirm}
          message={`¿Eliminar «${confirm?.label}»? Esta acción es irreversible.`}
          onCancel={()=>setConfirm(null)}
          onConfirm={doDelete}
        />

        {toast && <Toast message={toast.msg} variant={toast.varnt}/>}

      </main>
      <Footer/>
    </div>
  );
}
