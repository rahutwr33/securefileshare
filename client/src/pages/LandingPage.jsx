import React from 'react';
import { Link, Navigate } from 'react-router-dom';
import { Box, Typography, Button, Container } from '@mui/material';
import { useSelector } from 'react-redux';
const LandingPage = () => {
  const { isAuthenticated } = useSelector((state) => state.auth);
  if (isAuthenticated) {
    return <Navigate to="/dashboard" />;
  }
  return (
    <Container maxWidth="md" style={{ textAlign: 'center', marginTop: '50px' }}>
      <Typography variant="h2" gutterBottom>
        Welcome to SecureShare
      </Typography>
      <Typography variant="h5" gutterBottom>
        Your trusted platform for secure file sharing
      </Typography>
      <Typography variant="body1" paragraph>
        SecureShare offers a robust and secure way to share your files with others. 
        Our platform ensures your data is protected with top-notch security measures.
      </Typography>
      <Box mt={4}>
        <Button variant="contained" color="primary" component={Link} to="/login" style={{ marginRight: '10px' }}>
          Login
        </Button>
        <Button variant="outlined" color="primary" component={Link} to="/register">
          Register
        </Button>
      </Box>
    </Container>
  );
};

export default LandingPage; 