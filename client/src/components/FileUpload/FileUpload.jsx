import React, { useState, useRef } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  Box,
  Button,
  
  CircularProgress,
  Typography,
  Paper,
  LinearProgress,
  Alert,
} from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import { uploadFile } from '../../store/slices/userSlice';
import { encryptFile, generateEncryptionKey } from '../../utils/encryption';

const FileUpload = () => {
  const dispatch = useDispatch();
  const fileInput = useRef(null);
  const [selectedFile, setSelectedFile] = useState(null);
  const [progress, setProgress] = useState(0);
  const loading = useSelector(state => state.user.loading);
  const error = useSelector(state => state.user.error);
  const [showSuccess, setShowSuccess] = useState(false);

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file) {
      setSelectedFile(file);
      setShowSuccess(false);
    }
  };

  const handleUpload = async () => {
    const file = selectedFile;
      
    try {
      // Encrypt file before upload
      const key = await generateEncryptionKey();
      const { encryptedBlob, iv } = await encryptFile(file, key);  
      const exportedKey = await window.crypto.subtle.exportKey("raw", key);
       // Convert to Uint8Array
      const keyArray = new Uint8Array(exportedKey);
    // Encode key as Base64 for sending
      const keyBase64 = btoa(String.fromCharCode(...keyArray));

      // Create form data with encrypted file
      const formData = new FormData();
      formData.append("file", encryptedBlob, file.name);
      formData.append("iv", btoa(String.fromCharCode(...iv))); // Convert IV to Base64
      formData.append("user_key", keyBase64);
      // Upload with progress tracking
      await dispatch(uploadFile({
        formData,
        onProgress: (progress) => {
          setProgress(progress);
        },
      })).unwrap();

      setSelectedFile(null);
      setShowSuccess(true);
      setProgress(0);
      console.log("File uploaded successfully");
      
    } catch (err) {
      console.error(`Failed to upload ${file.name}:`, err);
    }
  };
  return (
    <Paper elevation={3} sx={{ maxWidth: 600, mx: 'auto',p:3 }}>
      <Box sx={{ textAlign: 'center' }}>
        {showSuccess && (
          <Alert 
            severity="success" 
            sx={{ mb: 2 }}
            onClose={() => setShowSuccess(false)}
          >
            File uploaded successfully!
          </Alert>
        )}
        {progress > 0 && (
          <Box sx={{ width: '100%', mb: 2 }}>
            <LinearProgress variant="determinate" value={progress} />
          </Box>
        )}
        <Box>
        <input
          type="file"
          ref={fileInput}
          onChange={handleFileSelect}
          style={{ display: 'none' }}
        />
        
        <Button
          variant="outlined"
          startIcon={<CloudUploadIcon />}
          onClick={() => fileInput.current.click()}
          disabled={loading}
          sx={{ }}
        >
          Select File
        </Button>

        <Button
          variant="contained"
          onClick={handleUpload}
          disabled={!selectedFile || loading}
          style={{marginLeft: 10}}
        >
          {loading ? (
            <>
              <CircularProgress size={24} sx={{ mr: 1 }} />
              Uploading...
            </>
          ) : (
            'Upload'
          )}
        </Button>
        </Box>

        {selectedFile && (
          <Typography variant="body2" sx={{ mb: 2 }}>
            Selected: {selectedFile.name}
          </Typography>
        )}

        {error && (
          <Typography color="error" sx={{ mt: 2 }}>
            {error}
          </Typography>
        )}
      </Box>
    </Paper>
  );
};

export default FileUpload; 