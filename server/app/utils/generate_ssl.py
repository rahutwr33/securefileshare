from OpenSSL import crypto
import os

def generate_self_signed_cert(cert_path="certificate.pem", key_path="private_key.pem"):
    """Generate a self-signed certificate and private key for development"""
    
    # Generate key
    key = crypto.PKey()
    key.generate_key(crypto.TYPE_RSA, 2048)
    
    # Generate certificate
    cert = crypto.X509()
    cert.get_subject().CN = "localhost"
    cert.set_serial_number(1000)
    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(365*24*60*60)  # Valid for one year
    cert.set_issuer(cert.get_subject())
    cert.set_pubkey(key)
    cert.sign(key, 'sha256')
    
    # Save certificate
    with open(cert_path, "wb") as f:
        f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))
    
    # Save private key
    with open(key_path, "wb") as f:
        f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, key))
    
    print(f"Generated SSL certificate: {cert_path}")
    print(f"Generated private key: {key_path}")

if __name__ == "__main__":
    # Create certs directory if it doesn't exist
    certs_dir = "certs"
    if not os.path.exists(certs_dir):
        os.makedirs(certs_dir)
    
    # Generate certificates in the certs directory
    cert_path = os.path.join(certs_dir, "certificate.pem")
    key_path = os.path.join(certs_dir, "private_key.pem")
    generate_self_signed_cert(cert_path, key_path) 