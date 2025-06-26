/* ------------------- Tema / Asignatura / Curso (DTO) ------------------- */
export interface Theme {
    id: number;
    title: string;
    description?: string;
    subject_id: number;
  }
  
  export interface Subject {
    id: number;
    name: string;
    description?: string;
    enrolled: boolean;
    themes: Theme[];
  }
  
  export interface Course {
    id: number;
    title: string;
    description: string | null;
    subjects: Subject[];
  }
  