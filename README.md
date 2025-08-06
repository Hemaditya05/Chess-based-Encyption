# Chess-Based Encryption

A full-stack, post-quantum secure encryption and decryption system combining chess-based key derivation, post-quantum cryptography, symmetric encryption, and steganography. Built with a React/Vite frontend and a FastAPI backend in Python.

---

## Features

- **Post-Quantum Security**  
  Utilizes Kyber512 KEM (via `liboqs-python`) for secure key encapsulation, ensuring resistance against quantum adversaries.

- **Chess-Based Key Derivation (ChessPerm)**  
  Generates high-entropy keys based on user-supplied chessboard permutations.

- **Authenticated Symmetric Encryption**  
  Uses XChaCha20-Poly1305 for fast and secure encryption with message authentication.

- **Steganography**  
  Embeds encrypted payloads into image files using LSB (Least Significant Bit) encoding techniques.

- **Modern User Interface**  
  A responsive and user-friendly frontend for seamless encryption and decryption workflows.

---

## Cryptographic Workflow

1. **Key Derivation (ChessPerm)**  
   Users input a sequence of chess moves or board states. These are deterministically transformed into a symmetric key.

2. **Key Encapsulation (Kyber512 KEM)**  
   The backend generates a Kyber512 public/private key pair.  
   The frontend uses the public key to encapsulate a shared secret.  
   This shared secret is used to derive the symmetric encryption key.

3. **Symmetric Encryption (XChaCha20-Poly1305)**  
   The user’s message is encrypted using XChaCha20 for confidentiality, with authentication provided by Poly1305.  
   The ciphertext, nonce, and MAC tag are bundled into a secure payload.

4. **Steganographic Embedding**  
   The encrypted payload is embedded into a user-provided PNG image using LSB steganography.  
   The final stego image is returned to the user for download or transmission.

5. **Decryption Process**  
   During decryption, the encrypted payload is extracted from the image.  
   The Kyber private key is used to decapsulate the shared secret, which is then used to decrypt and verify the original message.

---

## Project Structure

prototypeFinal/
├── README.md
├── backend/ # FastAPI backend (Python)
├── frontend/ # React + Vite frontend (TypeScript)
└── liboqs/ # Kyber post-quantum cryptography library (submodule or source)


---

## Setup Instructions

### 1. Backend (Python / FastAPI)

**Requirements**:  
- Python 3.9+  
- `liboqs-python`, `fastapi`, `uvicorn`, `pillow`, `cryptography`, `python-multipart`

**Steps**:
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload

Or run from the project root:

uvicorn backend.main:app --reload

2. Frontend (React / Vite)
Requirements:

Node.js 18+

npm

Steps:
cd frontend
npm install
npm run dev
Access the frontend at http://localhost:5173 (default Vite)

3. Configuration
Ensure the frontend API base URL matches the backend port (default: http://localhost:8000)

CORS is enabled in the backend for development use

Security Considerations
No plaintext keys or messages are stored at any point.

All cryptographic operations use secure, vetted libraries.

Steganography is intended for obfuscation, not cryptographic protection.

Acknowledgments
This project uses and builds upon:

liboqs-python

FastAPI

React

Vite

---


