from fastapi import Depends, HTTPException, status
from typing import List
from ..models.user import User, UserRole
from ..utils.auth import get_current_active_user

def check_role(allowed_roles: List[UserRole]):
    async def role_checker(current_user: User = Depends(get_current_active_user)):
        if current_user.role not in [role.value for role in allowed_roles]:  # Compare with string values
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to perform this action"
            )
        return current_user
    return role_checker

# Convenience dependencies
get_admin_user = check_role([UserRole.ADMIN])
get_any_user = check_role([UserRole.ADMIN, UserRole.USER])
