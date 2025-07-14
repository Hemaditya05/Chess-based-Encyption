# backend/main.py
import os, io, uuid, zipfile
from fastapi import FastAPI, Form, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

from .chessperm import derive_master_key
from .kyber_kem import generate_keypair, encapsulate, decapsulate
from .symcrypto import encrypt_message, decrypt_message
from .stego import embed_data_in_image, extract_data_from_image

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

BASE = os.path.dirname(__file__)
COVER = os.path.join(BASE, "cover.png")
TMP   = os.path.join(BASE, "tmp")
os.makedirs(TMP, exist_ok=True)

@app.post("/api/encrypt")
async def encrypt(pgn: str = Form(...), message: str = Form(...)):
    print("\n--- ENCRYPTION REQUEST ---")
    print(f"PGN: {pgn}")
    print(f"Message: {message}")
    # 1) ChessPerm → master key
    mk = derive_master_key(pgn)
    print(f"Master key (hex): {mk.hex()}")
    print(f"Master key length: {len(mk)} bytes")

    # 2) Kyber512 KEM
    pub, sec = generate_keypair()
    print(f"Public key (hex, truncated): {pub.hex()[:32]}... (len={len(pub)})")
    print(f"Secret key (hex, truncated): {sec.hex()[:32]}... (len={len(sec)})")
    kem_ct, shared = encapsulate(pub)
    print(f"KEM ciphertext (hex, truncated): {kem_ct.hex()[:32]}... (len={len(kem_ct)})")
    print(f"Shared secret (hex): {shared.hex()}")
    print(f"Shared secret length: {len(shared)} bytes")

    # 3) XOR with master key → symmetric key
    if len(mk) < len(shared):
        mk += b'\x00' * (len(shared) - len(mk))
    key = bytes(a ^ b for a, b in zip(shared, mk[:len(shared)]))
    print(f"Symmetric key (hex): {key.hex()}")
    print(f"Symmetric key length: {len(key)} bytes")

    # 4) Encrypt payload
    nonce, ct, tag = encrypt_message(key, message.encode())
    print(f"Nonce (hex): {nonce.hex()}")
    print(f"Tag (hex): {tag.hex()}")
    print(f"Ciphertext (hex, truncated): {ct.hex()[:32]}... (len={len(ct)})")
    payload = kem_ct + nonce + tag + ct
    print(f"Payload total length: {len(payload)} bytes")

    # 5) Stego-embed & write temp PNG
    img_out = os.path.join(TMP, f"{uuid.uuid4()}.png")
    embed_data_in_image(COVER, payload, img_out)

    # 6) ZIP { stego.png, private_key.txt }
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w') as z:
        z.write(img_out, arcname="stego.png")
        z.writestr("private_key.txt", sec.hex())
    buf.seek(0)

    print("--- ENCRYPTION COMPLETE ---\n")
    return StreamingResponse(
        buf,
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=chessperm_package.zip"}
    )

@app.post("/api/decrypt")
async def decrypt(
    file: UploadFile = File(...),
    private_key: str   = Form(...),
    pgn: str           = Form(...)
):
    print("\n--- DECRYPTION REQUEST ---")
    print(f"PGN: {pgn}")
    print(f"Private key (truncated): {private_key[:32]}... (len={len(private_key)})")
    try:
        # 1) Handle file upload - could be ZIP or PNG
        data = await file.read()
        print(f"Received file: {file.filename}, size: {len(data)} bytes")
        
        # Check if it's a ZIP file
        if file.filename and (file.filename.endswith('.zip') or file.content_type == 'application/zip'):
            try:
                with zipfile.ZipFile(io.BytesIO(data)) as zip_file:
                    if 'stego.png' not in zip_file.namelist():
                        print("ZIP file does not contain stego.png")
                        raise HTTPException(400, "ZIP file does not contain stego.png")
                    data = zip_file.read('stego.png')
                print("Extracted stego.png from ZIP")
            except zipfile.BadZipFile:
                print("Invalid ZIP file")
                raise HTTPException(400, "Invalid ZIP file")
        
        # 2) Save & extract stego
        img_in = os.path.join(TMP, f"{uuid.uuid4()}.png")
        with open(img_in, "wb") as f: 
            f.write(data)
        print(f"Saved stego image to: {img_in}")
        
        # Extract data from stego image
        blob = extract_data_from_image(img_in)
        print(f"Extracted blob length: {len(blob)}")
        if not blob:
            print("No data found in stego image")
            raise HTTPException(400, "No data found in stego image")

        # 3) Chop into (KEM_CT | nonce | tag | ct)
        LEN_KEM   = 768    # Kyber512 CT bytes (check your actual ciphertext length!)
        LEN_NONCE = 12
        LEN_TAG   = 16
        
        if len(blob) < LEN_KEM + LEN_NONCE + LEN_TAG:
            print(f"Invalid data length: {len(blob)} bytes")
            raise HTTPException(400, f"Invalid data length: {len(blob)} bytes")
            
        kem_ct    = blob[:LEN_KEM]
        nonce     = blob[LEN_KEM:LEN_KEM+LEN_NONCE]
        tag       = blob[LEN_KEM+LEN_NONCE:LEN_KEM+LEN_NONCE+LEN_TAG]
        ct        = blob[LEN_KEM+LEN_NONCE+LEN_TAG:]
        print(f"KEM_CT: {kem_ct.hex()[:32]}... (len={len(kem_ct)})")
        print(f"Nonce: {nonce.hex()}")
        print(f"Tag: {tag.hex()}")
        print(f"Ciphertext: {ct.hex()[:32]}... (len={len(ct)})")

        # 4) Decapsulate + rederive symmetric key
        try:
            shared = decapsulate(kem_ct, bytes.fromhex(private_key))
            print(f"Shared secret (hex): {shared.hex()}")
        except Exception as e:
            print(f"KEM decapsulation failed: {e}")
            raise HTTPException(400, f"KEM decapsulation failed: {str(e)}")
            
        mk = derive_master_key(pgn)
        if len(mk) < len(shared):
            mk += b'\x00' * (len(shared) - len(mk))
        key = bytes(a ^ b for a, b in zip(shared, mk[:len(shared)]))
        print(f"Symmetric key (hex): {key.hex()}")

        # 5) Decrypt & return
        try:
            pt = decrypt_message(key, nonce, ct, tag)
            print(f"Decrypted message: {pt.decode()}")
            print("--- DECRYPTION COMPLETE ---\n")
            return {"message": pt.decode()}
        except ValueError as e:
            print(f"Decryption failed: {e}")
            raise HTTPException(400, f"Decryption failed: {e}")
        except Exception as e:
            print(f"Decryption error: {e}")
            raise HTTPException(400, f"Decryption error: {str(e)}")
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"Internal server error: {e}")
        raise HTTPException(500, f"Internal server error: {str(e)}")
    finally:
        try:
            if 'img_in' in locals():
                os.remove(img_in)
        except:
            pass
