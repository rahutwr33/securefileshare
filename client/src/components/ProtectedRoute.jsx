import { Navigate, useLocation } from 'react-router-dom';
import { useSelector } from 'react-redux';
import MainLayout from '../components/Layout/MainLayout';

const ProtectedRoute = ({
  children,
  roles = [],
  permissions = []
}) => {
  const location = useLocation();
  const auth = useSelector(state => state.auth);
  if (auth.loading) {
    return <div>Loading...</div>;
  }

  if (!auth.isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }
  // Check roles
  if (roles.length > 0 && !roles.some(role => auth.roles.includes(role))) {
    return <Navigate to="/unauthorized" replace />;
  }
  
  // Check permissions
  if (permissions.length > 0 &&
    !permissions.some(permission => auth.permissions.includes(permission))) {
    return <Navigate to="/unauthorized" replace />;
  }

  return (
    <MainLayout>
      {children}
    </MainLayout>
  );
};

export default ProtectedRoute; 