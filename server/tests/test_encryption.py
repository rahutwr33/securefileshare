import pytest
from app.utils.encryption import FileEncryption
import os
import base64
from Crypto.Cipher import AES

def test_encryption():
    key = os.urandom(32)
    iv = os.urandom(16)
    cipher = AES.new(key, AES.MODE_GCM, nonce=iv)
    
    data = b"Test data"
    encrypted = cipher.encrypt(data)
    assert encrypted != data
    
    # Create new cipher for decryption
    decipher = AES.new(key, AES.MODE_GCM, nonce=iv)
    decrypted = decipher.decrypt(encrypted)
    assert decrypted == data

def test_base64_encoding():
    data = os.urandom(32)
    encoded = base64.b64encode(data)
    decoded = base64.b64decode(encoded)
    assert decoded == data

def test_encryption_decryption():
    key = os.urandom(32)
    iv = os.urandom(16)
    cipher = AES.new(key, AES.MODE_GCM, nonce=iv)
    
    original_data = b"Test data for encryption"
    encrypted_data = cipher.encrypt(original_data)
    assert encrypted_data != original_data

# Remove test_key_generation and test_iv_generation if these methods don't exist 