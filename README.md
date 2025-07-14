# Chess-based Encryption

A full-stack, post-quantum secure message encryption and decryption tool with steganography, built with a React/Vite frontend and a FastAPI Python backend.

---

## Features

- **Post-Quantum Security**: Uses Kyber512 KEM (via liboqs-python) for key encapsulation.
- **Chess-Based Key Derivation**: Derives keys from chessboard permutations (ChessPerm).
- **Symmetric Encryption**: XChaCha20-Poly1305 for authenticated encryption.
- **Steganography**: Hide encrypted data inside images.
- **Modern UI**: Responsive, user-friendly React interface.

---

## Cryptographic Workflow

### 1. **Key Derivation (ChessPerm)**
- Users input a chessboard permutation (e.g., FEN string or drag-and-drop board).
- This permutation is deterministically mapped to a symmetric key.

### 2. **Key Encapsulation (Kyber512 KEM)**
- The backend uses Kyber512 (via [liboqs-python](https://github.com/open-quantum-safe/liboqs-python)) to generate a public/private keypair.
- The frontend receives the public key and encapsulates a shared secret.
- The shared secret is used as the symmetric key for encryption.

### 3. **Symmetric Encryption (XChaCha20-Poly1305)**
- The message is encrypted using XChaCha20 for confidentiality and Poly1305 for authentication.
- The ciphertext, nonce, and MAC are bundled together.

### 4. **Steganography**
- The encrypted data is embedded into a user-supplied image (PNG) using LSB or similar techniques.
- The stego image is returned to the user for download or sharing.

### 5. **Decryption**
- The process is reversed: the backend extracts the encrypted data from the image, decapsulates the key, and decrypts the message.

---

## Project Structure

```
prototpyeFinal/
  README.md
  backend/           # FastAPI backend (Python)
  frontend/          # React/Vite frontend (JavaScript/TypeScript)
  liboqs/            # (Submodule or source) for post-quantum crypto
```

---

## Setup Instructions

### 1. **Backend (Python/FastAPI)**

- **Requirements**: Python 3.9+, `liboqs-python`, `fastapi`, `uvicorn`, `pillow`, `cryptography`, `python-multipart`
- **Install dependencies:**
  ```sh
  cd backend
  pip install -r requirements.txt
  ```
- **Run the backend:**
  ```sh
  uvicorn main:app --reload
  ```
  (Or, from project root: `uvicorn backend.main:app --reload`)

### 2. **Frontend (React/Vite)**

- **Requirements**: Node.js 18+, npm
- **Install dependencies:**
  ```sh
  cd frontend
  npm install
  ```
- **Run the frontend:**
  ```sh
  npm run dev
  ```
- The frontend will be available at [http://localhost:5173](http://localhost:5173) (default Vite port).

### 3. **Configuration**
- Ensure the frontend API base URL matches the backend port (default: 8000).
- CORS is enabled in the backend for local development.

---

## Security Notes
- **No plaintext keys or messages are stored.**
- **All cryptography is performed using vetted libraries.**
- **Steganography is for obfuscation, not security.**

---

## Credits
- [liboqs-python](https://github.com/open-quantum-safe/liboqs-python)
- [FastAPI](https://fastapi.tiangolo.com/)
- [React](https://react.dev/)
- [Vite](https://vitejs.dev/)

---

## License
MIT 