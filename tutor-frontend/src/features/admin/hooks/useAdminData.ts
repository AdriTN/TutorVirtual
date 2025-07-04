import { useMemo, useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useNotifications } from "@hooks/useNotifications";

import { useCourses } from "@features/explore/hooks/useCourses";
import { useSubjects } from "./useSubjects";
import { useAllThemes } from "./useThemes";

import {
  adminCreateCourse, adminUpdateCourse, adminDeleteCourse,
  adminAddSubjectToCourse, adminDetachSubjectsFromCourse,
  adminCreateSubject, adminUpdateSubject, adminDeleteSubject,
  adminAssignThemeToSubject, // Changed from adminAddThemeToSubject
  adminDetachThemesFromSubject,
  adminCreateTheme, adminUpdateTheme, adminDeleteTheme,
} from "@services/api/endpoints";
import { Theme } from "@/types";

export type ToastState =
  | { msg: string; varnt: "success" | "error" | "info" }
  | null;

export type AdminDataKind = "course" | "subject" | "theme";

export interface AdminDataItem {
  id: number;
  title?: string;
  name?: string;
  description?: string;
  subject_id?: number;
  [key: string]: any;
}

export function useAdminData() {
  const qc = useQueryClient();
  const { notifySuccess, notifyError } = useNotifications();

  /* ───── datos base ───── */
  const { data: courses = [], isLoading: loadingCourses } = useCourses();
  const { data: subjects = [], isLoading: loadingSubjects } = useSubjects();
  const { data: allThemes = [], isLoading: loadingThemes } = useAllThemes();

  /* ───── opciones & mapas ───── */
  const subjMap = useMemo(() => new Map(subjects.map(s => [s.id, s.name])), [subjects]);
  const courseOpts = useMemo(() => courses.map(c => ({ id: c.id, label: c.title })), [courses]);
  const subjectOpts = useMemo(() => subjects.map(s => ({ id: s.id, label: s.name })), [subjects]);

  const themeRows = useMemo(
    () => allThemes.map(t => ({
      id: t.id, title: t.title,
      description: t.description ?? "—",
      subject: subjMap.get(t.subject_id) ?? "—",
      subject_id: t.subject_id,
    })),
    [allThemes, subjMap],
  );

  /* ───── estado UI global para modales y notificaciones ───── */
  const [showCreateModal, setShowCreateModal] = useState<AdminDataKind | null>(null);
  const [editModalState, setEditModalState] = useState<{ kind: AdminDataKind; item: AdminDataItem } | null>(null);
  const [confirmDeleteModalState, setConfirmDeleteModalState] = useState<{ kind: AdminDataKind; id: number; label: string } | null>(null);


  /* ───── estado local para formularios de creación/edición ───── */
  // Común para varios formularios
  const [cTitle, setCTitle] = useState(""); const [cDesc, setCDesc] = useState("");
  const [cSubjectIds, setCSubjectIds] = useState<number[]>([]); // Para creación de curso
  const [sName, setSName] = useState(""); const [sDesc, setSDesc] = useState("");
  const [tSubj, setTSubj] = useState(""); const [tTitle, setTTitle] = useState("");
  const [tDesc, setTDesc] = useState("");

  const resetFormStates = () => {
    setCTitle(""); setCDesc(""); setCSubjectIds([]);
    setSName(""); setSDesc("");
    setTSubj(""); setTTitle(""); setTDesc("");
  };

  const openCreateModal = (kind: AdminDataKind) => {
    resetFormStates();
    setShowCreateModal(kind);
  };

  const closeCreateModal = () => {
    setShowCreateModal(null);
    resetFormStates();
  };

  const openEditModal = (kind: AdminDataKind, item: AdminDataItem) => {
    resetFormStates();
    if (kind === "course") { setCTitle(item.title ?? ""); setCDesc(item.description ?? ""); }
    if (kind === "subject") { setSName(item.name ?? ""); setSDesc(item.description ?? ""); }
    if (kind === "theme") {
      setTTitle(item.title ?? ""); setTDesc(item.description ?? "");
      setTSubj(String(item.subject_id ?? ""));
    }
    setEditModalState({ kind, item });
  };

  const closeEditModal = () => {
    setEditModalState(null);
    resetFormStates();
  };

  const openConfirmDeleteModal = (kind: AdminDataKind, id: number, label: string) => {
    setConfirmDeleteModalState({ kind, id, label });
  };

  const closeConfirmDeleteModal = () => {
    setConfirmDeleteModalState(null);
  };

  /* ================================================================
     MUTACIONES CRUD
  ================================================================ */

  // CREATE
  const createCourse = useMutation({
    mutationFn: () => adminCreateCourse({ title: cTitle, description: cDesc, subject_ids: cSubjectIds }),
    onSuccess: async () => {
      await qc.invalidateQueries({ queryKey: ["courses/all"], exact: true });
      closeCreateModal();
      notifySuccess("Curso creado");
    },
    onError: () => notifyError("Error al crear curso"),
  });

  const createSubject = useMutation({
    mutationFn: () => adminCreateSubject(sName, sDesc),
    onSuccess: async () => {
      await qc.invalidateQueries({ queryKey: ["subjects"], exact: true });
      closeCreateModal();
      notifySuccess("Asignatura creada");
    },
    onError: () => notifyError("Error al crear asignatura"),
  });

  const createTheme = useMutation({
    mutationFn: () => adminCreateTheme(tTitle, tDesc, +tSubj),
    onSuccess: async () => {
      await qc.invalidateQueries({ queryKey: ["all-themes"], exact: true });
      await qc.invalidateQueries({ queryKey: ["themes"], exact: true });
      closeCreateModal();
      notifySuccess("Tema creado");
    },
    onError: () => notifyError("Error al crear tema"),
  });

  // UPDATE
  const updateCourse = useMutation({
    mutationFn: (item: AdminDataItem) =>
      adminUpdateCourse(item.id, { title: cTitle, description: cDesc }),
    onSuccess: (item) => {
      qc.setQueryData(['courses/all'], (old: AdminDataItem[] = []) =>
        old.map(c =>
          c.id === item.data.id ? { ...c, title: cTitle, description: cDesc } : c
        )
      );
      qc.invalidateQueries({ queryKey: ['courses/all'], exact: true });
      notifySuccess('Curso actualizado');
      closeEditModal();
    },
    onError: () => notifyError("Error al actualizar curso"),
  });

  const updateSubject = useMutation({
    mutationFn: (item: AdminDataItem) =>
      adminUpdateSubject(item.id, { name: sName, description: sDesc }),
    onSuccess: async (item) => {
      qc.setQueryData(["subjects"], (old: AdminDataItem[] = []) =>
        old.map((s: AdminDataItem) =>
          s.id === item.data.id ? { ...s, name: sName, description: sDesc } : s
        )
      );
      await qc.invalidateQueries({ queryKey: ["subjects"], exact: true });
      notifySuccess("Asignatura actualizada");
      closeEditModal();
    },
    onError: () => notifyError("Error al actualizar asignatura"),
  });

  const updateTheme = useMutation({
    mutationFn: (item: AdminDataItem) =>
      adminUpdateTheme(item.id, {
        name: tTitle, description: tDesc, subject_id: +tSubj,
      }),
    onSuccess: async (item) => {
      qc.setQueryData(["all-themes"], (old: AdminDataItem[] = []) =>
        old.map((t: AdminDataItem) =>
          t.id === item.data.id
            ? { ...t, title: tTitle, description: tDesc, subject_id: +tSubj }
            : t
        )
      );
      await qc.invalidateQueries({ queryKey: ["all-themes"], exact: true });
      await qc.invalidateQueries({ queryKey: ["themes"], exact: true });
      notifySuccess("Tema actualizado");
      closeEditModal();
    },
    onError: () => notifyError("Error al actualizar tema"),
  });

  // DELETE
  const deleteCourse = useMutation({
    mutationFn: adminDeleteCourse,
    onSuccess: (_data, id: number) => {
      qc.setQueryData(['courses/all'], (old: AdminDataItem[] = []) =>
        old.filter(c => c.id !== id)
      );
      qc.invalidateQueries({ queryKey: ['courses/all'], exact: true });
      notifySuccess('Curso eliminado');
    },
    onError: () => notifyError("Error al eliminar curso"),
  });

  const deleteSubject = useMutation({
    mutationFn: adminDeleteSubject,
    onSuccess: async (_data, id: number) => {
      qc.setQueryData(["subjects"], (old: AdminDataItem[] = []) =>
        old.filter((s: AdminDataItem) => s.id !== id)
      );
      await qc.invalidateQueries({ queryKey: ["subjects"], exact: true });
      notifySuccess("Asignatura eliminada");
    },
    onError: () => notifyError("Error al eliminar asignatura"),
  });

  const deleteTheme = useMutation({
    mutationFn: adminDeleteTheme,
    onSuccess: async (_data, id: number) => {
      qc.setQueryData(["all-themes"], (old: AdminDataItem[] = []) =>
        old.filter((t: AdminDataItem) => t.id !== id)
      );
      await qc.invalidateQueries({ queryKey: ["all-themes"], exact: true });
      notifySuccess("Tema eliminado");
    },
    onError: () => notifyError("Error al eliminar tema"),
  });

  const handleDeleteConfirm = () => {
    if (!confirmDeleteModalState) return;
    const { kind, id } = confirmDeleteModalState;
    if (kind === "course") deleteCourse.mutate(id);
    if (kind === "subject") deleteSubject.mutate(id);
    if (kind === "theme") deleteTheme.mutate(id);
    closeConfirmDeleteModal();
  };


  /* ================================================================
     MUTACIONES VÍNCULOS
  ================================================================ */

  // Curso ↔ Asignatura
  const addSubjectToCourse = useMutation({
    mutationFn: ({ courseId, subjectId }: { courseId: number, subjectId: number }) =>
      adminAddSubjectToCourse(courseId, subjectId),
    onSuccess: async ({ data: { courseId, subjectId } }) => {
      qc.setQueryData(["courses/all"], (prev: AdminDataItem[] = []) =>
        prev.map(c =>
          c.id === courseId
            ? { ...c, subjects: [...(c.subjects || []), subjects.find(s => s.id === subjectId)!] }
            : c
        )
      );
      await qc.invalidateQueries({ queryKey: ["courses/all"], exact: true });
      notifySuccess("Asignatura añadida al curso");
    },
    onError: () => notifyError("Error al añadir asignatura al curso"),
  });

  const detachSubjectsFromCourse = useMutation({
    mutationFn: ({ courseId, subjectIds }: { courseId: number, subjectIds: number[] }) =>
      adminDetachSubjectsFromCourse(courseId, subjectIds),
    onSuccess: async ({ data: { courseId, subjectIds } }) => {
      qc.setQueryData(["courses/all"], (prev: AdminDataItem[] = []) =>
        prev.map(c =>
          c.id === courseId
            ? { ...c, subjects: (c.subjects || []).filter((s: any) => !subjectIds.includes(Number(s.id))) }
            : c
        )
      );
      await qc.invalidateQueries({ queryKey: ["courses/all"], exact: true });
      notifySuccess("Asignaturas desvinculadas del curso");
    },
    onError: () => notifyError("Error al desvincular asignaturas del curso"),
  });


  // Tema ↔ Asignatura
  const addThemeToSubject = useMutation({
    mutationFn: ({ subjectId, themeId }: { subjectId: number, themeId: number }) =>
      adminAssignThemeToSubject(subjectId, themeId), // Use the new service function
    onSuccess: async (data, { subjectId, themeId }) => {
      // The 'data' object here is the response from the new backend endpoint
      // which is the updated theme: { id, name, description, subject_id }
      // We should use this 'data' to update caches for consistency.

      // Update the cache for all themes
      qc.setQueryData(['all-themes'], (oldThemes: Theme[] = []) =>
        oldThemes.map(theme =>
          theme.id === themeId
            ? { ...theme, subject_id: subjectId, title: (data as any).name, description: (data as any).description } // Ensure structure matches Theme type
            : theme
        )
      );
      
      // Update the cache for the specific subject's theme list
      // Ensure the structure of 'data' matches AdminDataItem or transform it
      // For now, assuming 'data' can be cast or is compatible.
      // The backend returns {id, name, description, subject_id}.
      // Theme type is {id, title, description, subject_id}. AdminDataItem is similar.
      // We need to ensure the object added to ["themes", subjectId] is consistent.
      // The simplest is to refetch, but if optimistically updating:
      const themeForCache: AdminDataItem = {
        id: (data as any).id,
        title: (data as any).name, // Map 'name' from backend to 'title' for frontend AdminDataItem
        description: (data as any).description,
        subject_id: (data as any).subject_id,
        // Potentially other fields if AdminDataItem expects them, or ensure they are optional
      };

      qc.setQueryData(["themes", subjectId], (prev: AdminDataItem[] = []) => {
        // Avoid adding duplicates if already present due to optimistic update race conditions
        if (prev.find(t => t.id === themeForCache.id)) {
          return prev.map(t => t.id === themeForCache.id ? themeForCache : t);
        }
        return [...prev, themeForCache];
      });
      await qc.invalidateQueries({ queryKey: ["themes", subjectId], exact: true });
      await qc.invalidateQueries({ queryKey: ["all-themes"], exact: true });
      notifySuccess("Tema vinculado a la asignatura");
    },
    onError: () => notifyError("Error al vincular tema a la asignatura"),
  });

  const detachThemesFromSubject = useMutation({
    mutationFn: ({ subjectId, themeIds }: { subjectId: number, themeIds: number[] }) =>
      adminDetachThemesFromSubject(subjectId, themeIds),
    onSuccess: async ({ data: { subjectId, themeIds } }) => {
      qc.setQueryData(["themes", subjectId], (prev: AdminDataItem[] = []) =>
        prev.filter((t: any) => !themeIds.includes(Number(t.id)))
      );
      await qc.invalidateQueries({ queryKey: ["themes", subjectId], exact: true });
      await qc.invalidateQueries({ queryKey: ["all-themes"], exact: true });
      notifySuccess("Temas desvinculados de la asignatura");
    },
    onError: () => notifyError("Error al desvincular temas de la asignatura"),
  });


  return {
    // Datos
    courses, loadingCourses,
    subjects, loadingSubjects,
    allThemes, loadingThemes,
    themeRows,
    courseOpts, subjectOpts,

    // Estado UI para Modales y Toast
    showCreateModal, openCreateModal, closeCreateModal,
    editModalState, openEditModal, closeEditModal,
    confirmDeleteModalState, openConfirmDeleteModal, closeConfirmDeleteModal,

    // Estado de formularios (controlado por el hook)
    cTitle, setCTitle, cDesc, setCDesc, cSubjectIds, setCSubjectIds,
    sName, setSName, sDesc, setSDesc,
    tSubj, setTSubj, tTitle, setTTitle, tDesc, setTDesc,
    resetFormStates,

    // Mutaciones CRUD
    createCourse, createSubject, createTheme,
    updateCourse, updateSubject, updateTheme,
    deleteCourse, deleteSubject, deleteTheme,
    handleDeleteConfirm,

    // Mutaciones Vínculos
    addSubjectToCourse, detachSubjectsFromCourse,
    addThemeToSubject, detachThemesFromSubject,
  };
}
