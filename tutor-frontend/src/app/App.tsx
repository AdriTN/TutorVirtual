import { RouterProvider } from "react-router-dom";
import { router }         from "./routes";
import { ToastContainer } from "react-toastify";
import 'react-toastify/dist/ReactToastify.css';

import { AuthProvider }   from "@context/auth/AuthContext";
import { ViewModeProvider } from "@context/view-mode/ViewModeContext";

const App = () => (
  <AuthProvider>
    <ViewModeProvider>
      <RouterProvider router={router} />
      <ToastContainer />
    </ViewModeProvider>
  </AuthProvider>
);

export default App;