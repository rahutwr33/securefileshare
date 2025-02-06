import { configureStore } from '@reduxjs/toolkit';
import authReducer from './slices/authSlice';
import userReducer from './slices/userSlice';

const loadState = () => {
  try {
    const serializedState = localStorage.getItem('auth');
    if (serializedState === null) {
      return undefined;
    }
    return JSON.parse(serializedState);
  } catch (err) {
    return undefined;
  }
};

const localStorageMiddleware = store => next => action => {
  const result = next(action);
  const state = store.getState();
  try {
    const serializedState = JSON.stringify(state.auth);
    localStorage.setItem('auth', serializedState);
  } catch (err) {
    // Handle errors here
  }
  return result;
};

export const store = configureStore({
  reducer: {
    auth: authReducer,
    user: userReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware().concat(localStorageMiddleware),
  preloadedState: {
    auth: loadState(),
  },
});

// For use with useSelector and useDispatch hooks
export const getState = store.getState;
export const dispatch = store.dispatch; 