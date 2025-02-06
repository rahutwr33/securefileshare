// Define role hierarchy and permissions
export const ROLES = {
  ADMIN: 'admin',
  USER: 'user',
  GUEST: 'guest',
};

export const PERMISSIONS = {
  // File permissions
  FILE_UPLOAD: 'file_upload',
  FILE_DOWNLOAD: 'file:download',
  FILE_SHARE: 'file_share',
  FILE_DELETE: 'file:delete',
  
  // Admin permissions
  MANAGE_USERS: 'admin:users',
  MANAGE_FILES: 'admin:files',
  VIEW_ANALYTICS: 'admin:analytics',
};

// Role-based permissions mapping
export const ROLE_PERMISSIONS = {
  [ROLES.ADMIN]: [
    PERMISSIONS.MANAGE_USERS,
    PERMISSIONS.MANAGE_FILES,
    PERMISSIONS.VIEW_ANALYTICS,
  ],
  [ROLES.USER]: [
    PERMISSIONS.FILE_UPLOAD,
    PERMISSIONS.FILE_DOWNLOAD,
    PERMISSIONS.FILE_SHARE,
  ],
  [ROLES.GUEST]: [
    PERMISSIONS.FILE_DOWNLOAD,
  ],
};

// Helper functions to check permissions
export const hasPermission = (userPermissions, requiredPermission) => {
  return userPermissions.includes(requiredPermission);
};

export const hasRole = (userRoles, requiredRole) => {
  return userRoles.includes(requiredRole);
};

export const canAccess = (userRoles, userPermissions, requiredPermissions) => {
  // Admin has all permissions
  if (userRoles.includes(ROLES.ADMIN)) return true;
  
  // Check if user has any of the required permissions
  return requiredPermissions.some(permission => 
    userPermissions.includes(permission)
  );
}; 