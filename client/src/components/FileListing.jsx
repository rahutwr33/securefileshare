import React, { useState, useEffect } from 'react';
import {
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  CircularProgress,
  Box,
  Alert,
} from '@mui/material';
import {
  Delete,
  Share,
} from '@mui/icons-material';
import { useDispatch, useSelector } from 'react-redux';
import { fetchFiles, deleteFile } from '../store/slices/userSlice';
import FileDownload from './FileDownload';
import FileShare from './FileShare';

const FileListing = () => {
  const dispatch = useDispatch();
  const { files, loading, error } = useSelector(state => state.user);
  const {user}=useSelector(state=>state.auth)
  const [deleteDialog, setDeleteDialog] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [isShareDialogOpen, setIsShareDialogOpen] = useState(false);
  const [success, setSuccess] = useState(false);
  useEffect(() => {
    dispatch(fetchFiles());
  }, []);

  const handleDelete = async (fileId) => {
    try {
      await dispatch(deleteFile(fileId)).unwrap();
      setDeleteDialog(false);
      setSelectedFile(null);
      setSuccess(true);
      setTimeout(() => {
        setSuccess(false);
      }, 3000); 
    } catch (error) {
      console.error('Failed to delete file:', error);
    }
  };
  const handleShare = (fileId) => {
    setSelectedFile(fileId);
    setIsShareDialogOpen(true);
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" p={3}>
        <CircularProgress />
      </Box>
    );
  }
  return (
    <>
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}
      {success && (
        <Alert severity="success" sx={{ mt: 2 }} onClose={() => setSuccess(false)}>
          File deleted successfully!
        </Alert>
      )}
      <TableContainer component={Paper} sx={{mt: 2}}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>#</TableCell>
              <TableCell>File Name</TableCell>
              <TableCell>Size</TableCell>
              <TableCell>Uploaded At</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {files.length === 0 ? (
              <TableRow>
                <TableCell colSpan={6} align="center">
                  <Typography color="textSecondary">
                    No files found
                  </Typography>
                </TableCell>
              </TableRow>
            ) : (
              files.map((file,index) => (
                <TableRow key={file.id}>
                  <TableCell>{index + 1}</TableCell>
                  <TableCell>{file.filename}</TableCell>
                  <TableCell>{formatFileSize(file.size)}</TableCell>
                  <TableCell>
                    {new Date(file.upload_date).toLocaleDateString()}
                  </TableCell>
                 
                  <TableCell>
                  
                   {user.role === "user" && <>
                    <Tooltip title={"Share File"}>
                   <IconButton onClick={()=>handleShare(file.id)}>
                    <Share color="primary" />
                   </IconButton >
                   </Tooltip><FileDownload fileId={file.id} /></>}
                   {user.role==="admin" && <Tooltip title={"Delete File"}>
                      <IconButton onClick={()=>handleDelete(file.id)}>
                      <Delete color="error" />
                   </IconButton>
                   </Tooltip>}
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>

     { isShareDialogOpen && <FileShare isOpen={isShareDialogOpen} onClose={() => setIsShareDialogOpen(false)} fileId={selectedFile} />}
      
      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteDialog} onClose={() => setDeleteDialog(false)}>
        <DialogTitle>Confirm Delete</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to delete file "{selectedFile?.name}"?
            This action cannot be undone.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialog(false)}>Cancel</Button>
          <Button
            onClick={() => handleDelete(selectedFile?.id)}
            color="error"
            variant="contained"
          >
            Delete
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
};

export default FileListing;
