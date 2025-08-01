import io
import chess
import math
import hashlib

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

def derive_master_key_from_password(password: str) -> bytes:
    """
    Derive a master key from a password using the same block cipher logic as PGN.
    The password is converted to bits (ASCII), padded, and processed.
    """
    bits = []
    for byte in password.encode():
        for b in range(7, -1, -1):
            bits.append((byte >> b) & 1)
    blocks = _pad_bits(bits)
    processed = [_process_block(b) for b in blocks]
    final = processed[0]
    for blk in processed[1:]:
        final = [x ^ y for x, y in zip(final, blk)]
    return bytes(
        int(''.join(str(bit) for bit in final[i:i+8]), 2)
        for i in range(0, 256, 8)
    )

def _fen_to_bits(fen: str) -> list[int]:
    # Encode FEN string as bits (ASCII)
    bits = []
    for byte in fen.encode():
        for b in range(7, -1, -1):
            bits.append((byte >> b) & 1)
    return bits

def _chess_features_to_bits(board: chess.Board) -> list[int]:
    # Piece counts
    piece_counts = [board.piece_map().values().count(piece) if hasattr(board.piece_map().values(), 'count') else list(board.piece_map().values()).count(piece) for piece in [chess.PAWN, chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN, chess.KING]]
    bits = []
    for count in piece_counts:
        for b in range(4, -1, -1):
            bits.append((count >> b) & 1)
    # Castling rights
    for flag in [board.has_kingside_castling_rights(chess.WHITE), board.has_queenside_castling_rights(chess.WHITE), board.has_kingside_castling_rights(chess.BLACK), board.has_queenside_castling_rights(chess.BLACK)]:
        bits.append(int(flag))
    # En passant square
    ep = board.ep_square if board.ep_square is not None else 0
    for b in range(5, -1, -1):
        bits.append((ep >> b) & 1)
    return bits

def derive_master_key_robust(pgn: str, salt: bytes = b"", iterations: int = 1000) -> bytes:
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
    # Mix PGN bits, FEN bits, and chess features
    bits = _pgn_to_bits(pgn)
    bits += _fen_to_bits(board.fen())
    bits += _chess_features_to_bits(board)
    # Salt bits
    salt_bits = []
    for byte in salt:
        for b in range(7, -1, -1):
            salt_bits.append((byte >> b) & 1)
    # Pad and process
    blocks = _pad_bits(bits)
    state = [_process_block(b) for b in blocks]
    # Iterative mixing
    for i in range(iterations):
        for idx, block in enumerate(state):
            # XOR salt bits in each round
            block = [x ^ y for x, y in zip(block, salt_bits * (len(block)//len(salt_bits)+1))][:len(block)] if salt_bits else block
            block = _process_block(block)
            state[idx] = block
    # XOR-fold
    final = state[0]
    for blk in state[1:]:
        final = [x ^ y for x, y in zip(final, blk)]
    # Hash
    final_bytes = bytes(int(''.join(str(bit) for bit in final[i:i+8]), 2) for i in range(0, 256, 8))
    return hashlib.sha256(final_bytes).digest()

def derive_master_key_from_password_robust(password: str, salt: bytes = b"", iterations: int = 1000) -> bytes:
    bits = []
    for byte in password.encode():
        for b in range(7, -1, -1):
            bits.append((byte >> b) & 1)
    # Salt bits
    salt_bits = []
    for byte in salt:
        for b in range(7, -1, -1):
            salt_bits.append((byte >> b) & 1)
    blocks = _pad_bits(bits)
    state = [_process_block(b) for b in blocks]
    for i in range(iterations):
        for idx, block in enumerate(state):
            block = [x ^ y for x, y in zip(block, salt_bits * (len(block)//len(salt_bits)+1))][:len(block)] if salt_bits else block
            block = _process_block(block)
            state[idx] = block
    final = state[0]
    for blk in state[1:]:
        final = [x ^ y for x, y in zip(final, blk)]
    final_bytes = bytes(int(''.join(str(bit) for bit in final[i:i+8]), 2) for i in range(0, 256, 8))
    return hashlib.sha256(final_bytes).digest()
