import React from 'react';
import { IconButton, Tooltip } from '@mui/material';
import { Download } from '@mui/icons-material';
import axiosClient from '../utils/axios';

const FileDownload = ({ fileId }) => {
  const downloadFile = async () => {
    try {
      // Get the encrypted file data from the server
      const {data} = await axiosClient.get(`/user/download/${fileId}`);
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
      console.log("blob",blob)
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
  };

  return (
    <Tooltip title="Download File">
      <IconButton onClick={downloadFile}>
        <Download />
      </IconButton>
    </Tooltip>
  );
};

export default FileDownload; 