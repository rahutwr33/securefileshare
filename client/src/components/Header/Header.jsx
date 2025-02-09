import React from "react";
import { useNavigate } from "react-router-dom";
import { useDispatch, useSelector } from "react-redux";
import {
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  Avatar,
  Menu,
  MenuItem,
  Box
} from "@mui/material";
import {
  Person as PersonIcon,
  ExitToApp as LogoutIcon,
  Settings as SettingsIcon
} from "@mui/icons-material";
import { sessionExpired } from "../../store/slices/authSlice";
import axiosClient from "../../utils/axios";

const Header = () => {
  const navigate = useNavigate();
  const { user } = useSelector((state) => state.auth);
  const [anchorEl, setAnchorEl] = React.useState(null);
  const dispatch = useDispatch();

  const handleMenu = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const logoutUser = async () => {
    try {
      await axiosClient.post("/logout");
      dispatch(sessionExpired());
      localStorage.clear();

      setTimeout(() => {
        location.href = "/login";
      }, 1000);
    } catch (error) {
      console.error("Logout failed:", error);
    }
  };

  return (
    <AppBar position="static">
      <Toolbar>
        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
          Secure File Share
        </Typography>

        {user && (
          <Box>
            <IconButton size="large" onClick={handleMenu} color="inherit">
              <Avatar sx={{ width: 32, height: 32 }}>
                {user.username?.[0]?.toUpperCase() || <PersonIcon />}
              </Avatar>
            </IconButton>
            <Menu
              anchorEl={anchorEl}
              open={Boolean(anchorEl)}
              onClose={handleClose}
            >
              <MenuItem onClick={() => logoutUser()}>
                <LogoutIcon sx={{ mr: 1 }} /> Logout
              </MenuItem>
            </Menu>
          </Box>
        )}
      </Toolbar>
    </AppBar>
  );
};

export default Header;
