#!/usr/bin/env python3
"""Generate a private key for Connect IQ development"""

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend

# Generate private key
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
    backend=default_backend()
)

# Serialize private key to DER format
private_der = private_key.private_bytes(
    encoding=serialization.Encoding.DER,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption()
)

# Write to file
with open('developer_key.der', 'wb') as f:
    f.write(private_der)

print("Generated developer_key.der")