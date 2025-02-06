import base64
import os

def verify_key_length(key_b64):
    decoded = base64.b64decode(key_b64)
    print(f"Key length: {len(decoded)} bytes")
    return len(decoded)

# Generate a 32-byte key for AES-256
raw_key = os.urandom(32)  # Exactly 32 bytes
raw_iv = os.urandom(16)   # Exactly 16 bytes

aes_key = base64.b64encode(raw_key).decode()
aes_iv = base64.b64encode(raw_iv).decode()

print("\n=== GENERATED ENCRYPTION KEYS ===")
print("Copy these lines exactly into your .env file:\n")
print(f"SERVER_AES_KEY={aes_key}")
print(f"SERVER_AES_IV={aes_iv}")
print("\n=== END OF KEYS ===")

# Verify the lengths
decoded_key = base64.b64decode(aes_key)
decoded_iv = base64.b64decode(aes_iv)
print(f"\nVerification:")
print(f"Key length: {len(decoded_key)} bytes (should be 32)")
print(f"IV length: {len(decoded_iv)} bytes (should be 16)")

if len(decoded_key) != 32 or len(decoded_iv) != 16:
    print("\nWARNING: Key lengths are incorrect!") 