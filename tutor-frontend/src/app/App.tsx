import { RouterProvider } from "react-router-dom";
import { router }         from "./routes";

import { AuthProvider }   from "@context/auth/AuthContext";
import { ViewModeProvider } from "@context/view-mode/ViewModeContext";

const App = () => (
  <AuthProvider>
    <ViewModeProvider>
      <RouterProvider router={router} />
    </ViewModeProvider>
  </AuthProvider>
);

export default App;
