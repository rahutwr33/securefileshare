import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Box,
  Button,
  TextField,
  Typography,
  Container,
  Paper,
  Alert
} from "@mui/material";
import LockOutlinedIcon from "@mui/icons-material/LockOutlined";
import { sanitizeInput, validateEmail } from "../../utils/validation";
import axiosClient from "../../utils/axios";

const Login = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    email: "",
    password: ""
  });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prevState) => ({
      ...prevState,
      [name]: value
    }));
  };

  const validateForm = () => {
    const errors = {};

    // Sanitize and validate email
    const sanitizedEmail = sanitizeInput(formData.email);
    const emailError = validateEmail(sanitizedEmail);
    if (emailError) errors.email = emailError;

    // Basic password validation for login
    if (!formData.password) {
      errors.password = "Password is required";
    }

    setError(Object.values(errors)[0] || "");

    if (Object.keys(errors).length === 0) {
      // Update email with sanitized value
      setFormData((prev) => ({
        ...prev,
        email: sanitizedEmail
      }));
    }

    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    if (!validateForm()) {
      return;
    }

    setLoading(true);

    try {
      // Sanitize data before sending to server
      const sanitizedData = {
        email: sanitizeInput(formData.email),
        password: formData.password
      };

      const response = await axiosClient.post("/login", sanitizedData);
      console.log(response.data);
      // If successful, redirect to verification page with verification_id
      navigate("/login/verify", {
        state: {
          verification_id: response.data.verification_id,
          email: sanitizedData.email
        }
      });
    } catch (err) {
      setError(err.response?.data?.detail || "Login failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container component="main" maxWidth="xs">
      <Box
        sx={{
          marginTop: 8,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center"
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
            <LockOutlinedIcon sx={{ color: "white" }} />
          </Box>

          <Typography component="h1" variant="h5" sx={{ mb: 3 }}>
            Sign In
          </Typography>

          {error && (
            <Alert severity="error" sx={{ width: "100%", mb: 2 }}>
              {error}
            </Alert>
          )}

          <Box component="form" onSubmit={handleSubmit} sx={{ width: "100%" }}>
            <TextField
              margin="normal"
              required
              fullWidth
              id="email"
              label="Email Address"
              name="email"
              autoComplete="email"
              autoFocus
              value={formData.email}
              onChange={handleChange}
              error={!!error}
            />

            <TextField
              margin="normal"
              required
              fullWidth
              name="password"
              label="Password"
              type="password"
              id="password"
              autoComplete="current-password"
              value={formData.password}
              onChange={handleChange}
              error={!!error}
            />

            <Button
              type="submit"
              fullWidth
              variant="contained"
              disabled={loading}
              sx={{ mt: 3, mb: 2 }}
            >
              {loading ? "Signing in..." : "Sign In"}
            </Button>

            <Button
              fullWidth
              variant="text"
              onClick={() => navigate("/register")}
              sx={{ mb: 1 }}
            >
              Don't have an account? Sign Up
            </Button>
          </Box>
        </Paper>
      </Box>
    </Container>
  );
};

export default Login;
