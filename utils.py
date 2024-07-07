import os
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

def generate_keys():
    # Verifica se o diretório 'keys' existe, senão cria
    keys_dir = 'keys'
    if not os.path.exists(keys_dir):
        os.makedirs(keys_dir)

    # Gera o par de chaves RSA
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )
    public_key = private_key.public_key()
    
    # Salva a chave privada no arquivo 'keys/private.key'
    pem_private = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    )
    with open("keys/private.key", "wb") as private_file:
        private_file.write(pem_private)
    
    # Salva a chave pública no arquivo 'keys/public.key'
    pem_public = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    with open("keys/public.key", "wb") as public_file:
        public_file.write(pem_public)

def load_keys():
    # Carregar chave privada
    with open("keys/private.key", "rb") as private_file:
        private_key = serialization.load_pem_private_key(
            private_file.read(),
            password=None,
            backend=default_backend()
        )
    
    # Carregar chave pública
    with open("keys/public.key", "rb") as public_file:
        public_key = serialization.load_pem_public_key(
            public_file.read(),
            backend=default_backend()
        )
    
    return private_key, public_key

def encrypt_message(public_key, message):
    return public_key.encrypt(
        message,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

def decrypt_message(private_key, encrypted_message):
    return private_key.decrypt(
        encrypted_message,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
