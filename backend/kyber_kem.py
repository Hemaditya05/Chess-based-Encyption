# backend/kyber_kem.py
import oqs

def generate_keypair():
    kem = oqs.KeyEncapsulation('Kyber512')
    public_key = kem.generate_keypair()
    secret_key = kem.export_secret_key()
    return public_key, secret_key

def encapsulate(public_key: bytes):
    kem = oqs.KeyEncapsulation('Kyber512')
    ciphertext, shared_secret = kem.encap_secret(public_key)
    return ciphertext, shared_secret

def decapsulate(ciphertext: bytes, secret_key: bytes):
    # This is the correct way to initialize the KEM object for decapsulation with a given secret key
    kem = oqs.KeyEncapsulation('Kyber512', secret_key=secret_key)
    shared_secret = kem.decap_secret(ciphertext)
    return shared_secret