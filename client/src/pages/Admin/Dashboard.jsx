import React, { useState } from 'react';
import { Box, Container, Tabs, Tab, Typography } from '@mui/material';
import UserListing from '../../components/UserListing';
import FileListing from '../../components/FileListing';
import { useSelector } from 'react-redux';

const AdminDashboard = () => {
  const [currentTab, setCurrentTab] = useState(0);
  const {user}=useSelector(state=>state.auth)
  const handleTabChange = (event, newValue) => {
    setCurrentTab(newValue);
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <div>
      Hello Admin:- <span style={{fontSize:'1.2rem',fontWeight:'bold', color:'blue', textAlign:'center'}}>{user.full_name}</span>
      </div>
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={currentTab} onChange={handleTabChange}>
          <Tab label="Users" />
          <Tab label="Files" />
        </Tabs>
      </Box>
      {currentTab === 0 && <UserListing />}
      {currentTab === 1 && <FileListing />}
      
    </Container>
  );
};

export default AdminDashboard; 