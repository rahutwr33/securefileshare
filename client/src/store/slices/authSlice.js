import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import axiosClient from '../../utils/axios';


export const logout = createAsyncThunk(
  'auth/logout',
  async (_, { rejectWithValue }) => {
    try {
      await axiosClient.post('/logout');
      location.href = '/login';
      return { success: true };
    } catch (error) {
      location.href = '/login';
      return rejectWithValue(error.response?.data?.message || 'Logout failed');
    }
  }
);

export const fetchUserData = createAsyncThunk(
  '/me',
  async (_, { dispatch }) => {
    try {
      console.log("fetching user data")
      const response = await axiosClient.get('/profile');
      if (!response.data) {
        dispatch(sessionExpired());
      }
    } catch (error) {
      console.log(error)
    }
  }
);

export const ROLES = {
  ADMIN: 'admin',
  USER: 'user',
  GUEST: 'guest'
}

const authSlice = createSlice({
  name: 'auth',
  initialState: {
    user: null,
    isAuthenticated: false,
    loading: false,
    error: null,
    roles: [],
    permissions: []
  },
  reducers: {
    setUser: (state, action) => {
      state.user = action.payload;
      state.isAuthenticated = !!action.payload;
      state.error = null;
    },
    setRoles: (state, action) => {
      state.roles = action.payload;
    },
    setPermissions: (state, action) => {
      state.permissions = action.payload;
    },
    sessionExpired: (state) => {
      state.user = null;
      state.isAuthenticated = false;
      state.roles = [];
      state.permissions = [];
      state.error = 'Session expired. Please login again.';
    },
    clearUser: (state) => {
      state.user = null;
    },
    clearRoles: (state) => {
      state.roles = [];
    },
    clearPermissions: (state) => {
      state.permissions = [];
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(logout.fulfilled, (state) => {
        state.user = null;
        state.isAuthenticated = false;
        state.roles = [];
        state.permissions = [];
      })

  },
});

export const { setUser, clearUser, setRoles, setPermissions, clearRoles, clearPermissions, sessionExpired } = authSlice.actions;
export default authSlice.reducer; 