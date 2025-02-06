import { store } from '../store';
import { fetchUserData } from '../store/slices/authSlice';

class SessionManager {
  constructor() {
    this.tokenKey = 'token';
  }

  initialize(dispatch) {
   dispatch(fetchUserData())
  }

  setSession(token) {
    try {
      if (token) {
        localStorage.setItem(this.tokenKey, token);
      } else {
        this.clearSession();
      }
    } catch (error) {
      console.error('Error setting session:', error);
      this.clearSession();
    }
  }

  getToken() {
    try {
      return localStorage.getItem(this.tokenKey);
    } catch {
      return null;
    }
  }

  clearSession() {
    try {
      this.tokenKey=null;
      localStorage.clear();
    } catch (error) {
      console.error('Error clearing session:', error);
    }
  }
}

export const sessionManager = new SessionManager(); 