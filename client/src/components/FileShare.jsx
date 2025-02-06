import React, { useState, useEffect } from 'react';

import axiosClient from '../utils/axios';
import {
    Button,
    Select,
    MenuItem,
    Box,
    FormControl,
    InputLabel,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    Snackbar,
    Alert
} from '@mui/material';

const FileShare = ({ isOpen, onClose, fileId }) => {
    const [users, setUsers] = useState([]);
    const [selectedUser, setSelectedUser] = useState(null);
    const [permission, setPermission] = useState('view');
    const [loading, setLoading] = useState(false);
    const [expiration, setExpiration] = useState(900);
    const [open, setOpen] = useState(false);
    const [message, setMessage] = useState('');
    useEffect(() => {
        fetchUsers();
    }, []);

    const fetchUsers = async () => {
        try {
            const response = await axiosClient('/user/users');
            setUsers(response.data);
        } catch (error) {
            console.log(error);
        }
    };

    const handleShare = async () => {
        if (!selectedUser) {
            console.log('Please select a user');
            return;
        }
        setLoading(true);
        try {
            const response = await axiosClient.post(`/user/share`, {
                "file_id": fileId,
                "user_id": selectedUser,
                "expires_in_seconds": expiration,
                "permission": permission
              });
            if (response.status === 200) {
                setMessage('File shared successfully');
                setOpen(true);
               setTimeout(() => {
                onClose();
               }, 3000);
            }
        } catch (error) {
            setMessage('Failed to share file');
            setOpen(true);
        } finally {
            setLoading(false);
        }
    };

    const permissionOptions = [
        { value: 'view', label: 'View Only' },
        { value: 'download', label: 'Download' },
    ];
    return (
        <>
            {open && <Snackbar open={open} autoHideDuration={6000} onClose={() => setOpen(false)}>
                <Alert severity={message.includes('success') ? 'success' : 'error'}>{message}</Alert>
            </Snackbar>}
            <Dialog
                open={isOpen}
                onClose={onClose}
                maxWidth="sm"
                fullWidth
            >
                <DialogTitle>Share File</DialogTitle>
                <DialogContent>
                    <Box sx={{ mt: 2 }}>
                        <FormControl fullWidth sx={{ mb: 3 }}>
                            <InputLabel id="user-select-label">Select User</InputLabel>
                            <Select
                                labelId="user-select-label"
                                value={selectedUser || ''}
                                label="Select User"
                                onChange={(e) => setSelectedUser(e.target.value)}
                            >
                                {users.map(user => (
                                    <MenuItem key={user.id} value={user.id}>
                                        {user.name}
                                    </MenuItem>
                                ))}
                            </Select>
                        </FormControl>

                        <FormControl fullWidth>
                            <InputLabel id="permission-select-label">Permission</InputLabel>
                            <Select
                                labelId="permission-select-label"
                                value={permission}
                                label="Permission"
                                onChange={(e) => setPermission(e.target.value)}
                            >
                                {permissionOptions.map(option => (
                                    <MenuItem key={option.value} value={option.value}>
                                        {option.label}
                                    </MenuItem>
                                ))}
                            </Select>
                        </FormControl>

                        <FormControl fullWidth sx={{ mt: 2 }}>
                            <InputLabel id="expiration-select-label">Expiration</InputLabel>
                            <Select
                                labelId="expiration-select-label"
                                value={expiration}
                                label="Expiration"
                                onChange={(e) => setExpiration(e.target.value)}
                            >
                                <MenuItem value={900}>15 Minutes</MenuItem>
                                <MenuItem value={1800}>30 Minutes</MenuItem>
                                <MenuItem value={3600}>1 Hour</MenuItem>
                                <MenuItem value={7200}>2 Hours</MenuItem>
                                <MenuItem value={14400}>4 Hours</MenuItem>
                                <MenuItem value={28800}>8 Hours</MenuItem>
                                <MenuItem value={43200}>12 Hours</MenuItem>
                                <MenuItem value={86400}>1 Day</MenuItem>
                            </Select>
                        </FormControl>
                    </Box>
                </DialogContent>

                <DialogActions>
                    <Button onClick={onClose} color="inherit">
                        Cancel
                    </Button>
                    <Button
                        onClick={handleShare}
                        variant="contained"
                        disabled={loading}
                    >
                        {loading ? 'Sharing...' : 'Share'}
                    </Button>
                </DialogActions>
            </Dialog>
        </>

    );
};

export default FileShare;
