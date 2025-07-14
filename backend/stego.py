from PIL import Image

_TERMINATOR = '1111111111111110'

def embed_data_in_image(input_path: str, data: bytes, output_path: str) -> str:
    img = Image.open(input_path)
    encoded = img.copy()
    w, h = img.size

    bits = ''.join(f'{b:08b}' for b in data) + _TERMINATOR
    idx = 0

    for y in range(h):
        for x in range(w):
            if idx >= len(bits):
                break
            px = list(img.getpixel((x, y)))
            for i in range(3):
                if idx < len(bits):
                    px[i] = (px[i] & ~1) | int(bits[idx])
                    idx += 1
            encoded.putpixel((x, y), tuple(px))
        if idx >= len(bits):
            break

    encoded.save(output_path)
    return output_path

def extract_data_from_image(input_path: str) -> bytes:
    try:
        img = Image.open(input_path)
        bits = ''

        for y in range(img.height):
            for x in range(img.width):
                px = img.getpixel((x, y))
                for i in range(3):
                    bits += str(px[i] & 1)
                    if bits.endswith(_TERMINATOR):
                        data_bits = bits[:-len(_TERMINATOR)]
                        # Ensure we have complete bytes
                        if len(data_bits) % 8 != 0:
                            return b''
                        return bytes(
                            int(data_bits[i:i+8], 2)
                            for i in range(0, len(data_bits), 8)
                        )
        return b''
    except Exception as e:
        print(f"Error extracting data from image: {e}")
        return b''
