import { createBrowserRouter, Navigate } from "react-router-dom";

import HomePage       from "@features/landing/pages/Landing";
import LoginPage      from "@features/auth/pages/login/LoginPage";
import RegisterPage   from "@features/auth/pages/register/RegisterPage";
import DashboardPage  from "@features/dashboard/pages/Dashboard";
import CoursesPage    from "@features/explore/pages/Courses";
import CourseSubjects from "@features/explore/pages/Subjects";
import ConfirmPage    from "@features/explore/pages/Confirm";
import StudyPage      from "@features/study/pages/StudyPage";
import StatsPage      from "@features/stats/pages/StatsPage";
import AdminDashboard from "@features/admin/pages/AdminDashboard";
import MyCourseSubjectsPage   from "@features/my-subjects/pages/MySubjects";
import ThemesPage     from "@features/themes/pages/ThemesPage";

import PrivateRoute from "./guards/PrivateRoute";
import GuestRoute   from "./guards/GuestRoute";
import AdminRoute   from "./guards/AdminRoute";
import { MyCoursesPage } from "@/features/my-courses";

export const router = createBrowserRouter([
  /* ————————————————— PÚBLICO ————————————————— */
  { path: "/", element: <HomePage /> },

  /* ——————————— SOLO VISITANTES ——————————— */
  {
    element: <GuestRoute />,
    children: [
      { path: "/login",    element: <LoginPage /> },
      { path: "/register", element: <RegisterPage /> },
    ],
  },

  /* ——————————— USUARIO LOGUEADO ——————————— */
  {
    element: <PrivateRoute />,
    children: [
      { path: "/dashboard",                                element: <DashboardPage /> },
      { path: "/my-courses",                               element: <MyCoursesPage  /> },
      { path: "/my-subjects/:courseId",                    element: <MyCourseSubjectsPage  /> },
      { path: "/my-subjects/:courseId/:subjectId/themes",  element: <ThemesPage  /> },
      { path: "/courses",                                  element: <CoursesPage  /> },
      { path: "/courses/:id",                              element: <CourseSubjects /> },
      { path: "/courses/:id/confirm",                      element: <ConfirmPage /> },
      { path: "/study/:courseId/:subjectId",               element: <StudyPage /> },
      { path: "/stats",                                    element: <StatsPage /> },
      { path: "/auth/google/callback",                     element: <Navigate to="/dashboard" replace /> },

    ],
  },

  /* ——————————— ADMIN ——————————— */
  {
    element: <AdminRoute />,
    children: [
      { path: "/admin", element: <AdminDashboard /> },
    ],
  },

  /* ——————————— CATCH-ALL ——————————— */
  { path: "*", element: <Navigate to="/" replace /> },
]);
