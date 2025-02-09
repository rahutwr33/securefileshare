import { useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import { Provider } from "react-redux";
import { store } from "./store";
import {
  CircularProgress,
  Box,
  CssBaseline,
  ThemeProvider,
  createTheme
} from "@mui/material";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import LoginPage from "./pages/Auth/Login";
import LandingPage from "./pages/LandingPage";
import RegisterPage from "./pages/Auth/Register";
import LoginVerify from "./pages/Auth/LoginVerify";
import Dashboard from "./pages/Dashboard";
import NotFound from "./pages/Auth/NotFound";
import ProtectedRoute from "./components/ProtectedRoute";
import UnauthorizedPage from "./pages/UnauthorizedPage";
import { ROLE_PERMISSIONS, ROLES } from "./utils/rbac";
import AdminDashboard from "./pages/Admin/Dashboard";
import FileView from "./components/FileView";
// Create theme instance
const theme = createTheme({
  palette: {
    primary: {
      main: "#1976d2"
    },
    secondary: {
      main: "#dc004e"
    },
    background: {
      default: "#f5f5f5"
    }
  }
});

// Move all Redux-dependent logic into AppContent
const AppContent = () => {
  const { loading } = useSelector((state) => state.auth);

  if (loading) {
    return (
      <Box
        display="flex"
        justifyContent="center"
        alignItems="center"
        minHeight="100vh"
      >
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/login/verify" element={<LoginVerify />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route
        path="/dashboard"
        element={
          <ProtectedRoute
            roles={[ROLES.USER]}
            permissions={ROLE_PERMISSIONS[ROLES.USER]}
          >
            <Dashboard />
          </ProtectedRoute>
        }
      />
      <Route
        path="/admin/*"
        element={
          <ProtectedRoute roles={[ROLES.ADMIN]}>
            <AdminDashboard />
          </ProtectedRoute>
        }
      />
      <Route path="/file/:link/:flag" element={<FileView />} />
      <Route path="/unauthorized" element={<UnauthorizedPage />} />
      <Route path="*" element={<NotFound />} />
    </Routes>
  );
};

// App component needs to provide Router at the top level
const App = () => {
  return (
    <Provider store={store}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Router>
          <AppContent />
        </Router>
      </ThemeProvider>
    </Provider>
  );
};

export default App;
