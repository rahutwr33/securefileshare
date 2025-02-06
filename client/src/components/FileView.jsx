import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import axiosClient from "../utils/axios";
import { Box, Typography, Button, } from '@mui/material';
const FileView = () => {
    const { link, flag } = useParams();
    const [file, setFile] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchFile = async () => {
            try {
                setLoading(true);
                const response = await axiosClient.get(`/user/shared/${link}`);
                if (response.status === 200) {
                    setFile(response.data);
                } else {
                    setError(response.data);
                }
                setLoading(false);
            } catch (error) {
                console.log(error?.response?.data?.detail);
                setError(error?.response?.data?.detail || "An error occurred while fetching the file");
            } finally {
                setLoading(false);
            }
        };
        fetchFile();
    }, [link]);

    if (loading) {
        return <div>Loading...</div>;
    }

    if (error) {
        return <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100vh' }}>

            <Typography
                variant="h6"
                sx={{
                    marginTop: 2,
                    color: 'red',
                    fontWeight: 'bold',
                }}
            >
                {error}
            </Typography>
            <Button onClick={() => window.location.href = '/'}>Go to Home</Button>
        </div>;
    }

    const downloadFile = async (fileId) => {
        try {
            // Get the encrypted file data from the server
            const { data } = await axiosClient.get(`/user/download/${fileId}`);
            // Decode Base64 values
            const encryptedData = new Uint8Array(atob(data.encrypted_data).split("").map(c => c.charCodeAt(0)));
            const iv = new Uint8Array(atob(data.iv).split("").map(c => c.charCodeAt(0)));
            const tag = new Uint8Array(atob(data.tag).split("").map(c => c.charCodeAt(0)));
            const keyBuffer = Uint8Array.from(atob(data.key), c => c.charCodeAt(0));
            // Import key for Web Crypto API
            const key = await crypto.subtle.importKey(
                "raw",
                keyBuffer,
                { name: "AES-GCM" },
                false,
                ["decrypt"]
            );
            const combinedCiphertext = new Uint8Array(encryptedData.length + tag.length);
            combinedCiphertext.set(encryptedData);
            combinedCiphertext.set(tag, encryptedData.length);
            // Decrypt the file
            const decryptedBuffer = await crypto.subtle.decrypt(
                { name: "AES-GCM", iv: iv },
                key,
                combinedCiphertext
            );
            // Convert decrypted data to Blob and trigger download
            const blob = new Blob([decryptedBuffer], { type: "application/octet-stream" });
            console.log("blob", blob)
            const link = document.createElement("a");
            link.href = URL.createObjectURL(blob);
            link.download = data.filename;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            console.log("File decrypted and downloaded successfully");
        } catch (error) {
            console.error('Error downloading files123', error);
            alert('Failed to download file');
        }
    }

    const renderFile = () => {
        if (['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'svg', "image/webp", "image/svg+xml", "image/jpeg", "image/png", "image/gif", "image/bmp"].includes(file.file_type)) {
            return <img src={`data:${file.file_type};base64,${file.decrypted_data}`} alt="File" style={{ width: 500, height: 500 }} />
        } else if (file.file_type == "application/pdf") {
            const pdfUrl = `data:application/pdf;base64,${file.decrypted_data}`
            return <iframe src={pdfUrl} alt="File" style={{ width: 500, height: 500 }} />
        } else if (['mp4', 'webm', 'ogg'].includes(file.file_type)) {
            return <video src={`data:video/mp4;base64,${file.decrypted_data}`} alt="File" style={{ width: 500, height: 500 }} />
        } else {
            return <div>{file.decrypted_data}</div>
        }
    }
    return (
        <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 2 }}>
            <Typography variant="h6">{file.filename}</Typography>
            {file.permission === "download" && <Button
                variant="contained"
                color="primary"
                onClick={() => downloadFile(file.id)}
            >
                Download
            </Button>}

            {/* This is the area where the file content will be rendered */}
            {renderFile()}


        </Box>
    );
};

export default FileView;
