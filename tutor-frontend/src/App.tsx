import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import RegisterPage from "./pages/register/RegisterPage";
import LoginPage from "./pages/login/LoginPage";
import Home from "./pages/home/Home";
import { AuthProvider } from "./context/AuthContext";
import PrivateRoute from "./routes/PrivateRoute";
import Dashboard from "./pages/dashboard/Dashborad";
import GuestRoute from "./routes/GuestRoute";
import CoursesPage from "./pages/explore/Courses";
import ConfirmPage from "./pages/explore/Confirm";
import SubjectsPage from "./pages/explore/Subjects";
import MyCoursesPage from "./pages/mycourses/MyCourses";
import MyCourseSubjectsPage from "./pages/mysubjects/MySubjects";
import ThemesPage from "./pages/themes/ThemesPage";
import StudyPage from "./pages/study/StudyPage";
import AdminDashboard from "./pages/admin/AdminDashboard";
import AdminRoute from "./routes/AdminRoute";
import { ViewModeProvider } from "./context/ViewModeContext";

function App() {
  return (
    <AuthProvider>
      <ViewModeProvider>
        <BrowserRouter>
          <Routes>
            <Route 
              path="/" 
              element={
              <Home />
              } 
            />
            <Route 
              path="/register" 
              element={
              <GuestRoute>
                <RegisterPage />
              </GuestRoute>
              } 
            />
            <Route 
              path="/login" 
              element={
              <GuestRoute>
                <LoginPage />
              </GuestRoute>
              } 
            />
            <Route
              path="/dashboard"
              element={
                <PrivateRoute>
                  <Dashboard />
                </PrivateRoute>
              }
            />
            <Route
              path="/my-courses"
              element={
                <PrivateRoute>
                  <MyCoursesPage />
                </PrivateRoute>
              }
            />
            <Route
              path="/my-subjects/:id"
              element={
                <PrivateRoute>
                  <MyCourseSubjectsPage />
                </PrivateRoute>
              }
            />
            <Route
              path="/my-subjects/:courseId/:subjectId/themes"
              element={
                <PrivateRoute>
                  <ThemesPage />
                </PrivateRoute>
              }
            />
            <Route
              path="/courses"
              element={
                <PrivateRoute>
                  <CoursesPage />
                </PrivateRoute>
              }
            />
            <Route
              path="/courses/:id"
              element={
                <PrivateRoute>
                  <SubjectsPage />
                </PrivateRoute>
              }
            />
            <Route
              path="/courses/:id/confirm"
              element={
                <PrivateRoute>
                  <ConfirmPage />
                </PrivateRoute>
              }
            />
            <Route
              path="/study/:courseId/:subjectId"
              element={
                <PrivateRoute>
                  <StudyPage />
                </PrivateRoute>
              }
            />
            <Route
              path="/admin"
              element={
                <AdminRoute>
                  <AdminDashboard />
                </AdminRoute>
              }
            />

            <Route 
              path="*" 
              element={
              <Navigate to="/" />
              } 
            />
          </Routes>
        </BrowserRouter>
      </ViewModeProvider>
    </AuthProvider>
  );
}

export default App;
