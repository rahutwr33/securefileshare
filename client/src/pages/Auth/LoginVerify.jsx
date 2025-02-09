import React, { useState, useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { useDispatch } from "react-redux";
import {
  Box,
  Button,
  TextField,
  Typography,
  Container,
  Paper,
  Alert,
  CircularProgress
} from "@mui/material";
import VerifiedUserIcon from "@mui/icons-material/VerifiedUser";
import {
  setUser,
  setRoles,
  setPermissions
} from "../../store/slices/authSlice";
import axiosClient from "../../utils/axios";
import { ROLE_PERMISSIONS, ROLES } from "../../utils/rbac";

const LoginVerify = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const dispatch = useDispatch();

  const [verificationCode, setVerificationCode] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [timeLeft, setTimeLeft] = useState(600); // 10 minutes in seconds
  const [successMessage, setSuccessMessage] = useState("");

  // Get verification_id from location state
  const verification_id = location.state?.verification_id;
  const email = location.state?.email;

  // Redirect if no verification_id
  useEffect(() => {
    if (!verification_id || !email) {
      navigate("/login");
    }
  }, [verification_id, email, navigate]);

  // Countdown timer
  useEffect(() => {
    if (timeLeft <= 0) return;

    const timer = setInterval(() => {
      setTimeLeft((prev) => prev - 1);
    }, 1000);

    return () => clearInterval(timer);
  }, [timeLeft]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSuccessMessage("");

    if (!verificationCode) {
      setError("Please enter the verification code");
      return;
    }

    setLoading(true);

    try {
      const response = await axiosClient.post("/verify-login", {
        verification_id,
        code: verificationCode
      });

      // Only store the token in localStorage
      dispatch(setUser(response.data.user));
      // Store user info in Redux
      if (response.data.user.role === "admin") {
        dispatch(setRoles(ROLES.ADMIN));
        dispatch(setPermissions(ROLE_PERMISSIONS[ROLES.ADMIN]));
      } else if (response.data.user.role === "user") {
        dispatch(setRoles(ROLES.USER));
        dispatch(setPermissions(ROLE_PERMISSIONS[ROLES.USER]));
      } else if (response.data.user.role === "guest") {
        dispatch(setRoles(ROLES.GUEST));
        dispatch(setPermissions(ROLE_PERMISSIONS[ROLES.GUEST]));
      }

      // Set success message
      setSuccessMessage("Verification successful! Redirecting...");
      setTimeout(() => {
        // Redirect based on user role
        if (response.data.user?.role === "admin") {
          navigate("/admin");
        } else {
          navigate("/dashboard");
        }
      }, 2000);
    } catch (err) {
      console.log(err);
      setError(
        err.response?.data?.detail || "Verification failed. Please try again."
      );
    } finally {
      setLoading(false);
    }
  };

  if (!verification_id || !email) {
    return null; // Will redirect via useEffect
  }

  return (
    <Container component="main" maxWidth="xs">
      <Box
        sx={{
          marginTop: 8,
          display: "flex",
          flexDirection: "column",
          alignItems: "center"
        }}
      >
        <Paper
          elevation={3}
          sx={{
            padding: 4,
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            width: "100%"
          }}
        >
          <Box
            sx={{
              backgroundColor: "primary.main",
              borderRadius: "50%",
              padding: 1,
              marginBottom: 1
            }}
          >
            <VerifiedUserIcon sx={{ color: "white" }} />
          </Box>

          <Typography component="h1" variant="h5" sx={{ mb: 1 }}>
            Verify Login
          </Typography>

          <Typography
            variant="body2"
            color="textSecondary"
            sx={{ mb: 3, textAlign: "center" }}
          >
            Please enter the verification code sent to your email
          </Typography>

          {error && (
            <Alert severity="error" sx={{ width: "100%", mb: 2 }}>
              {error}
            </Alert>
          )}

          {successMessage && (
            <Alert severity="success" sx={{ width: "100%", mb: 2 }}>
              {successMessage}
            </Alert>
          )}

          <Box component="form" onSubmit={handleSubmit} sx={{ width: "100%" }}>
            <TextField
              margin="normal"
              required
              fullWidth
              name="verificationCode"
              label="Verification Code"
              type="text"
              id="verificationCode"
              autoComplete="one-time-code"
              value={verificationCode}
              onChange={(e) => setVerificationCode(e.target.value)}
              autoFocus
            />

            <Typography
              variant="body2"
              color="textSecondary"
              sx={{ mt: 1, mb: 2 }}
            >
              Time remaining: {Math.floor(timeLeft / 60)}:
              {(timeLeft % 60).toString().padStart(2, "0")}
            </Typography>

            <Button
              type="submit"
              fullWidth
              variant="contained"
              disabled={loading || timeLeft <= 0}
              sx={{ mb: 2 }}
            >
              {loading ? <CircularProgress size={24} /> : "Verify"}
            </Button>
          </Box>
        </Paper>
      </Box>
    </Container>
  );
};

export default LoginVerify;
