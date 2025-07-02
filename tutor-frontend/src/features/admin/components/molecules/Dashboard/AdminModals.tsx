import { CrudModal, ConfirmDialog, SelectField } from "@features/admin/components";
import Spinner from "@components/atoms/Spinner/Spinner";
import styles from "../../../pages/AdminDashboard.module.css";
import { AdminDataKind, AdminDataItem, useAdminData } from "@features/admin/hooks/useAdminData";

interface AdminModalsProps {
  adminData: ReturnType<typeof useAdminData>;
  subjectOpts: { id: number; label: string }[];
}

export function AdminModals({ adminData, subjectOpts }: AdminModalsProps) {
  const {
    showCreateModal, closeCreateModal,
    editModalState, closeEditModal,
    confirmDeleteModalState, closeConfirmDeleteModal, handleDeleteConfirm,

    cTitle, setCTitle, cDesc, setCDesc,
    sName, setSName, sDesc, setSDesc,
    tSubj, setTSubj, tTitle, setTTitle, tDesc, setTDesc,

    createCourse, createSubject, createTheme,
    updateCourse, updateSubject, updateTheme,
  } = adminData;

  const currentEditItem = editModalState?.item;

  return (
    <>
      {/* ====== MODALES DE CREACIÓN ====== */}
      <CrudModal open={showCreateModal === "course"} title="Nuevo curso" onClose={closeCreateModal}>
        <input
          value={cTitle} onChange={e => setCTitle(e.target.value)} placeholder="Título" />
        <textarea
          value={cDesc} onChange={e => setCDesc(e.target.value)} placeholder="Descripción" />
        <div className={styles.actions}>
          <button onClick={closeCreateModal}>Cancelar</button>
          <button disabled={!cTitle.trim() || createCourse.isPending}
            onClick={() => createCourse.mutate()}>
            {createCourse.isPending ? <Spinner size={16} /> : "Guardar"}
          </button>
        </div>
      </CrudModal>

      <CrudModal open={showCreateModal === "subject"} title="Nueva asignatura" onClose={closeCreateModal}>
        <input
          value={sName} onChange={e => setSName(e.target.value)} placeholder="Nombre" />
        <textarea
          value={sDesc} onChange={e => setSDesc(e.target.value)} placeholder="Descripción" />
        <div className={styles.actions}>
          <button onClick={closeCreateModal}>Cancelar</button>
          <button disabled={!sName.trim() || createSubject.isPending}
            onClick={() => createSubject.mutate()}>
            {createSubject.isPending ? <Spinner size={16} /> : "Guardar"}
          </button>
        </div>
      </CrudModal>

      <CrudModal open={showCreateModal === "theme"} title="Nuevo tema" onClose={closeCreateModal}>
        <SelectField id="subj4themeCreate" label="Asignatura"
          value={tSubj} onChange={v => setTSubj(String(v))} options={subjectOpts} />
        <input
          value={tTitle} onChange={e => setTTitle(e.target.value)} placeholder="Título" />
        <textarea
          value={tDesc} onChange={e => setTDesc(e.target.value)} placeholder="Descripción" />
        <div className={styles.actions}>
          <button onClick={closeCreateModal}>Cancelar</button>
          <button disabled={!tSubj || !tTitle.trim() || createTheme.isPending}
            onClick={() => createTheme.mutate()}>
            {createTheme.isPending ? <Spinner size={16} /> : "Guardar"}
          </button>
        </div>
      </CrudModal>

      {/* ====== MODAL DE EDICIÓN ====== */}
      <CrudModal open={!!editModalState} title={`Editar ${editModalState?.kind || ''}`} onClose={closeEditModal}>
        {editModalState?.kind === "course" && currentEditItem && (
          <>
            <input
              value={cTitle} onChange={e => setCTitle(e.target.value)} placeholder="Título" />
            <textarea
              value={cDesc} onChange={e => setCDesc(e.target.value)} placeholder="Descripción" />
            <div className={styles.actions}>
              <button onClick={closeEditModal}>Cancelar</button>
              <button disabled={updateCourse.isPending}
                onClick={() => updateCourse.mutate(currentEditItem)}>
                {updateCourse.isPending ? <Spinner size={16} /> : "Guardar"}
              </button>
            </div>
          </>
        )}

        {editModalState?.kind === "subject" && currentEditItem && (
          <>
            <input
              value={sName} onChange={e => setSName(e.target.value)} placeholder="Nombre" />
            <textarea
              value={sDesc} onChange={e => setSDesc(e.target.value)} placeholder="Descripción" />
            <div className={styles.actions}>
              <button onClick={closeEditModal}>Cancelar</button>
              <button disabled={updateSubject.isPending}
                onClick={() => updateSubject.mutate(currentEditItem)}>
                {updateSubject.isPending ? <Spinner size={16} /> : "Guardar"}
              </button>
            </div>
          </>
        )}

        {editModalState?.kind === "theme" && currentEditItem && (
          <>
            <SelectField id="editThemeSubj" label="Asignatura"
              value={tSubj} onChange={v => setTSubj(String(v))} options={subjectOpts} />
            <input
              value={tTitle} onChange={e => setTTitle(e.target.value)} placeholder="Título" />
            <textarea
              value={tDesc} onChange={e => setTDesc(e.target.value)} placeholder="Descripción" />
            <div className={styles.actions}>
              <button onClick={closeEditModal}>Cancelar</button>
              <button disabled={updateTheme.isPending}
                onClick={() => updateTheme.mutate(currentEditItem)}>
                {updateTheme.isPending ? <Spinner size={16} /> : "Guardar"}
              </button>
            </div>
          </>
        )}
      </CrudModal>

      {/* ====== MODAL DE CONFIRMACIÓN DE BORRADO ====== */}
      <ConfirmDialog
        open={!!confirmDeleteModalState}
        message={`¿Eliminar «${confirmDeleteModalState?.label}»? Esta acción es irreversible.`}
        onCancel={closeConfirmDeleteModal}
        onConfirm={handleDeleteConfirm}
      />
    </>
  );
}
