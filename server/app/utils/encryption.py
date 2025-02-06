from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
import os
import base64
import json

class FileEncryption:
    def __init__(self):
        self.backend = default_backend()
        self.master_key = os.getenv('ENCRYPTION_MASTER_KEY', os.urandom(32))  # Master key for server-side encryption
        self.key_size = 32  # 256 bits

    def decrypt_client_side(self, encrypted_content: bytes, encryption_meta: dict) -> bytes:
        """
        Decrypt content that was encrypted on the client side using Web Crypto API
        Args:
            encrypted_content: The encrypted file content
            encryption_meta: Dict containing 'iv' from client
        """
        # Convert IV from bytes to the format needed by cryptography
        iv = encryption_meta['iv']
        
        # Since we're not decrypting (client keeps the key), just return the content as-is
        # The content will remain encrypted with the client's key
        return encrypted_content

    def server_side_encrypt(self, content: bytes) -> bytes:
        """
        Server-side encryption using AES-256-GCM
        Returns the encrypted content with IV and auth tag
        """
        iv = os.urandom(16)
        
        cipher = Cipher(
            algorithms.AES(self.master_key),
            modes.GCM(iv),
            backend=self.backend
        )
        encryptor = cipher.encryptor()
        
        # Encrypt the content
        encrypted_content = encryptor.update(content) + encryptor.finalize()
        
        # Combine IV + encrypted content + auth tag for storage
        return iv + encryptor.tag + encrypted_content

    def server_side_decrypt(self, encrypted_data: bytes) -> bytes:
        """
        Decrypt server-side encrypted file
        Expects data in format: IV + auth_tag + encrypted_content
        """
        iv = encrypted_data[:16]
        auth_tag = encrypted_data[16:32]
        encrypted_content = encrypted_data[32:]

        cipher = Cipher(
            algorithms.AES(self.master_key),
            modes.GCM(iv, auth_tag),
            backend=self.backend
        )
        decryptor = cipher.decryptor()
        return decryptor.update(encrypted_content) + decryptor.finalize() 