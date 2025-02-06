import { useSelector } from 'react-redux';
import { canAccess } from '../utils/rbac';
import { ROLES } from '../utils/rbac';

const Permission = ({ 
  permissions = [], 
  roles = [], 
  children, 
  fallback = null 
}) => {
  const {  auth } = useSelector(state => state);
  const { user } = auth;

  // Check if the user has any of the required permissions
  const hasPermission = permissions.some(permission => {
    if (user.role === ROLES.ADMIN) {
      return true; // Admins have all permissions
    }
    // Implement logic to check if the user has the specific permission
    return auth.permissions.includes(permission);
  });

  const hasRequiredRole = roles.length === 0 || 
    roles.some(role => auth.roles.includes(role));

  if (hasPermission && hasRequiredRole) {
    return children;
  }

  return fallback;
};

export default Permission; 