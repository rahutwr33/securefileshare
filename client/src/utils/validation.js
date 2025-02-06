// Input sanitization and validation utilities

export const sanitizeInput = (input) => {
  // Implement input sanitization
  // Remove potentially dangerous characters
  // Validate input format
  if (typeof input !== 'string') return '';
  return input.trim().replace(/<[^>]*>/g, '');
};

export const validateEmail = (email) => {
  if (!email) return 'Email is required';
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(email)) {
    return 'Please enter a valid email address';
  }
  return '';
};

export const validateUsername = (username) => {
  // Username format validation
  const usernameRegex = /^[a-zA-Z0-9._-]{3,30}$/;
  
  if (!username) return 'Username is required';
  username = sanitizeInput(username);
  
  if (username.length < 3) {
    return 'Username must be at least 3 characters long';
  }
  
  if (username.length > 30) {
    return 'Username must be less than 30 characters';
  }
  
  if (!usernameRegex.test(username)) {
    return 'Username can only contain letters, numbers, and .-_';
  }
  
  return '';
};

export const validatePassword = (password) => {
  if (!password) return 'Password is required';
  
  const errors = [];
  
  // Length check
  if (password.length < 8) {
    errors.push('at least 8 characters');
  }
  
  // Uppercase check
  if (!/[A-Z]/.test(password)) {
    errors.push('one uppercase letter');
  }
  
  // Lowercase check
  if (!/[a-z]/.test(password)) {
    errors.push('one lowercase letter');
  }
  
  // Number check
  if (!/\d/.test(password)) {
    errors.push('one number');
  }
  
  // Special character check
  if (!/[!@#$%^&*]/.test(password)) {
    errors.push('one special character (!@#$%^&*)');
  }
  
  // Return formatted error message
  return errors.length > 0 
    ? `Password must contain ${errors.join(', ')}`
    : '';
};

export const validateConfirmPassword = (password, confirmPassword) => {
  if (!confirmPassword) return 'Please confirm your password';
  if (password !== confirmPassword) return 'Passwords do not match';
  return '';
}; 