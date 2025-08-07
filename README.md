 


# Chess-Based Encryption

A full-stack, post-quantum secure encryption and decryption system that combines chess-based key derivation, post-quantum cryptography, authenticated symmetric encryption, and steganography.

Built with a modern **React + Vite** frontend and a **FastAPI (Python)** backend.



## Features

- **Post-Quantum Security**  
  Utilizes **Kyber512 KEM** (via `liboqs-python`) for secure key encapsulation and resistance against quantum adversaries.

- **Chess-Based Key Derivation (ChessPerm)**  
  Generates high-entropy symmetric keys from chessboard permutations or SAN/PGN move sequences.

- **Authenticated Symmetric Encryption**  
  Encrypts data using **XChaCha20-Poly1305**, offering fast, secure, and authenticated encryption.

- **Steganography Support**  
  Embeds encrypted payloads into PNG images using Least Significant Bit (LSB) encoding.

- **Modern User Interface**  
  Fully interactive and responsive frontend built with **React**, supporting both encryption and decryption workflows.

---

## Cryptographic Workflow

1. **Key Derivation (ChessPerm)**  
   User-supplied chess moves or board positions are deterministically converted into a 256-bit symmetric key.

2. **Key Encapsulation (Kyber512)**  
   A Kyber512 public/private key pair is generated. The public key is used to encapsulate a shared secret, which is XORed with the master key to derive the final encryption key.

3. **Symmetric Encryption**  
   The message is encrypted using **XChaCha20**, authenticated via **Poly1305**, producing a secure payload (nonce + tag + ciphertext).

4. **Steganographic Embedding**  
   The encrypted payload is embedded inside a PNG image using LSB steganography. The result is a visually unchanged image containing the hidden data.

5. **Decryption Process**  
   The payload is extracted from the stego image. Using the Kyber private key and the same master key derivation, the original message is securely decrypted and verified.

---

## Project Structure

```

chess-based-encryption/
├── README.md
├── backend/         # FastAPI backend (Python)
├── frontend/        # React + Vite frontend (TypeScript)
├── liboqs/          # Kyber PQC (as submodule or installed separately)

````

---

## Setup Instructions

### Backend (Python / FastAPI)

**Requirements:**
- Python 3.9+
- `liboqs-python`, `fastapi`, `uvicorn`, `pillow`, `cryptography`, `python-multipart`

**Steps:**
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
````

Or from project root:

```bash
uvicorn backend.main:app --reload
```

---

### Frontend (React / Vite)

**Requirements:**

* Node.js 18+
* npm

**Steps:**

```bash
cd frontend
npm install
npm run dev
```

Access the frontend at:
[http://localhost:5173](http://localhost:5173)

---

## Configuration Notes

* Ensure the **frontend API base URL** matches the backend port (default: `http://localhost:8000`).
* **CORS** is enabled in the FastAPI backend for development use.

---

## Security Considerations

* No plaintext keys or messages are stored.
* All cryptographic operations use vetted, standard libraries.
* Steganography is used for obfuscation—not as a replacement for cryptographic confidentiality.

---

## Acknowledgments

This project builds upon the following open-source tools and libraries:

* [liboqs-python](https://github.com/open-quantum-safe/liboqs-python)
* [FastAPI](https://fastapi.tiangolo.com/)
* [React](https://reactjs.org/)
* [Vite](https://vitejs.dev/)

---

## License

This project is licensed under the MIT License.


