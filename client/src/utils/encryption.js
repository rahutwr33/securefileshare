export const generateEncryptionKey = async () => {
  return await window.crypto.subtle.generateKey(
    { name: "AES-GCM", length: 256 },
    true,
    ["encrypt", "decrypt"]
);
};

export async  function encryptFile(file, key) {
  const iv = window.crypto.getRandomValues(new Uint8Array(12)); // Generate IV
    const fileBuffer = await file.arrayBuffer();

    const encryptedBuffer = await window.crypto.subtle.encrypt(
        { name: "AES-GCM", iv: iv },
        key,
        fileBuffer
    );

    // Convert encrypted file to Blob
    const encryptedBlob = new Blob([encryptedBuffer], { type: file.type });

    return { encryptedBlob, iv };
}


export const decryptFile = async (encryptedBlob, keyArray, ivArray) => {
  try {
    // Convert key array back to ArrayBuffer
    const keyBuffer = new Uint8Array(keyArray).buffer;
    
    // Import the key
    const key = await window.crypto.subtle.importKey(
      'raw',
      keyBuffer,
      'AES-GCM',
      true,
      ['decrypt']
    );

    // Convert IV array back to Uint8Array
    const iv = new Uint8Array(ivArray);

    // Get encrypted data as ArrayBuffer
    const encryptedData = await encryptedBlob.arrayBuffer();

    // Decrypt the data
    const decryptedData = await window.crypto.subtle.decrypt(
      {
        name: 'AES-GCM',
        iv: iv,
      },
      key,
      encryptedData
    );

    return new Blob([decryptedData]);
  } catch (error) {
    console.error('Decryption failed:', error);
    throw new Error('Failed to decrypt file');
  }
}; 