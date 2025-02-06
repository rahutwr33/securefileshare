import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import axiosClient from '../../utils/axios';


export const fetchFiles = createAsyncThunk(
  'user/fetchFiles',
  async (_, { rejectWithValue }) => {
    try {
      const response = await axiosClient.get('/user/files');
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data);
    }
  }
);

export const deleteFile = createAsyncThunk(
  'user/deleteFile',
  async (fileId, { rejectWithValue }) => {
    try {
      await axiosClient.delete(`/admin/file/${fileId}`);
      return fileId;
    } catch (error) {
      return rejectWithValue(error.response?.data);
    }
  }
);


export const fetchUsers = createAsyncThunk(
  'user/fetchUsers',
  async (_, { rejectWithValue }) => {
    try {
      const response = await axiosClient.get('/admin/users');
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data);
    }
  }
);

export const deleteUser = createAsyncThunk(
  'user/deleteUser',
  async (userId, { rejectWithValue }) => {
    try {
      await axiosClient.delete(`/admin/users/${userId}`);
      return userId;
    } catch (error) {
      return rejectWithValue(error.response?.data);
    }
  }
);


export const uploadFile = createAsyncThunk(
  'file/upload',
  async ({ formData, onProgress }, { rejectWithValue }) => {
    try {
      const response = await axiosClient.post('/user/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          const percentCompleted = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          );
          onProgress?.(percentCompleted);
        },
      });

      return {
        ...response.data,
        encryptionKey: formData.get('encryptionMeta')
      };
    } catch (error) {
      return rejectWithValue(error.response?.data?.message || 'Upload failed');
    }
  }
);

export const shareFile = createAsyncThunk(
  'files/share',
  async ({ fileId, expiryHours, permission }, { rejectWithValue }) => {
    try {
      const response = await axios.post(`/api/user/share/${fileId}`, {
        expiry_hours: expiryHours,
        permission,
      });
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || 'Sharing failed');
    }
  }
);


const userSlice = createSlice({
  name: 'user',
  initialState: {
    files: [],
    users: [],
    loading: false,
    error: null,
    currentFile: null,
    uploadProgress: {},
  },
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
    setCurrentFile: (state, action) => {
      state.currentFile = action.payload;
    },
    clearError: (state) => {
      state.error = null;
    },
    setUploadProgress: (state, action) => {
      const { fileId, progress } = action.payload;
      state.uploadProgress[fileId] = progress;
    },
    addFile: (state, action) => {
      state.files=[action.payload,...state.files]
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch Files
      .addCase(fetchFiles.pending, (state) => {
        state.loading = true;
      })
      .addCase(fetchFiles.fulfilled, (state, action) => {
        state.loading = false;
        state.files = action.payload;
      })
      .addCase(fetchFiles.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })

      // Fetch Users
      .addCase(fetchUsers.pending, (state) => {
        state.loading = true;
      })
      .addCase(fetchUsers.fulfilled, (state, action) => {
        state.loading = false;
        state.users = action.payload;
      })
      .addCase(fetchUsers.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })

      // Delete File
      .addCase(deleteFile.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(deleteFile.fulfilled, (state, action) => {
        state.files = state.files.filter(file => file.id !== action.payload);
        state.loading = false;
        state.error = null;
      })
      .addCase(deleteFile.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })

      // Delete User
      .addCase(deleteUser.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(deleteUser.fulfilled, (state, action) => {
        state.users = state.users.filter(user => user.id !== action.payload);
        state.loading = false;  
        state.error = null;
      })
      .addCase(deleteUser.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })

      .addCase(uploadFile.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(uploadFile.fulfilled, (state, action) => {
        console.log(action.payload)
        const  {id,filename,size,upload_date}=action.payload
        state.loading = false;
        state.files=[{id,filename,size,upload_date},...state.files]
      })
      .addCase(uploadFile.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })

  },
});

export const { setCurrentFile, clearError, setUploadProgress, addFile } = userSlice.actions;
export default userSlice.reducer; 