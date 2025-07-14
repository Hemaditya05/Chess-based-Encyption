import io
import chess
import math

# 4-bit S-box for Pawn substitution
_SBOX = [
    0x6, 0xB, 0xC, 0x0,
    0x5, 0x7, 0xA, 0xD,
    0x1, 0xF, 0x3, 0x9,
    0xE, 0x8, 0x4, 0x2,
]

def _pgn_to_bits(pgn: str) -> list[int]:
    bits = []
    board = chess.Board()
    for token in pgn.replace('\n', ' ').split(' '):
        token = token.strip()
        if not token or token.endswith('.'):
            continue
        try:
            move = board.parse_san(token)
        except ValueError:
            continue
        board.push(move)
        uci = move.uci()
        coords = [
            ord(uci[0]) - ord('a'),
            ord(uci[1]) - ord('1'),
            ord(uci[2]) - ord('a'),
            ord(uci[3]) - ord('1'),
        ]
        for coord in coords:
            for b in (2, 1, 0):
                bits.append((coord >> b) & 1)
    return bits

def _pad_bits(bits: list[int], block_size: int = 256) -> list[list[int]]:
    rem = len(bits) % block_size
    if rem:
        bits += [0] * (block_size - rem)
    return [bits[i:i+block_size] for i in range(0, len(bits), block_size)]

def _rotate(arr: list[int], n: int) -> list[int]:
    n %= len(arr)
    return arr[n:] + arr[:n]

def _knight_jump(block: list[int]) -> list[int]:
    size = int(math.isqrt(len(block)))
    out = block.copy()
    for idx in range(len(block)):
        r, c = divmod(idx, size)
        r2 = (r + 2) % size
        c2 = (c + 1) % size
        idx2 = r2 * size + c2
        out[idx], out[idx2] = block[idx2], block[idx]
    return out

def _pawn_substitution(block: list[int]) -> list[int]:
    out = []
    for i in range(0, len(block), 4):
        nibble = (block[i] << 3) | (block[i+1] << 2) | (block[i+2] << 1) | block[i+3]
        sub = _SBOX[nibble]
        for b in (3, 2, 1, 0):
            out.append((sub >> b) & 1)
    return out

def _rook_diffusion(block: list[int]) -> list[int]:
    size = int(math.isqrt(len(block)))
    out = block.copy()
    # rows
    for r in range(size):
        start = r * size
        row = out[start:start+size]
        shift = sum(row) % size
        out[start:start+size] = _rotate(row, shift)
    # columns
    for c in range(size):
        col = [out[r*size + c] for r in range(size)]
        shift = sum(col) % size
        rotated = _rotate(col, shift)
        for r in range(size):
            out[r*size + c] = rotated[r]
    return out

def _promotion_nonlinearity(block: list[int], round_idx: int) -> list[int]:
    idx = round_idx % len(block)
    block[idx] ^= 1
    return block

def _process_block(block: list[int]) -> list[int]:
    b = block.copy()
    for rnd in range(16):
        b = _knight_jump(b)
        b = _pawn_substitution(b)
        b = _rook_diffusion(b)
        b = _promotion_nonlinearity(b, rnd)
    return b

def derive_master_key(pgn: str) -> bytes:
    bits = _pgn_to_bits(pgn)
    if not bits:
        # fallback to raw ASCII bits
        for byte in pgn.encode():
            for b in range(7, -1, -1):
                bits.append((byte >> b) & 1)

    blocks = _pad_bits(bits)
    processed = [_process_block(b) for b in blocks]

    # XOR-fold multiple blocks
    final = processed[0]
    for blk in processed[1:]:
        final = [x ^ y for x, y in zip(final, blk)]

    # pack into 32 bytes
    return bytes(
        int(''.join(str(bit) for bit in final[i:i+8]), 2)
        for i in range(0, 256, 8)
    )
