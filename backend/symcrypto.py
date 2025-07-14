from Crypto.Cipher import ChaCha20_Poly1305

def encrypt_message(key: bytes, plaintext: bytes):
    cipher = ChaCha20_Poly1305.new(key=key)
    ciphertext, tag = cipher.encrypt_and_digest(plaintext)
    return cipher.nonce, ciphertext, tag

def decrypt_message(key: bytes, nonce: bytes, ciphertext: bytes, tag: bytes):
    cipher = ChaCha20_Poly1305.new(key=key, nonce=nonce)
    return cipher.decrypt_and_verify(ciphertext, tag)
