import chess
import secrets

def _password_to_bits(password: str, salt: bytes = b'') -> list[int]:
    combined = password.encode() + salt
    return [((byte >> i) & 1) for byte in combined for i in reversed(range(8))]

def _get_chunk_val(bits: list[int], index: int, chunk_size: int = 6) -> int:
    start = (index * chunk_size) % len(bits)
    chunk = bits[start:start + chunk_size]
    if len(chunk) < chunk_size:
        chunk += bits[:chunk_size - len(chunk)]
    return int(''.join(str(b) for b in chunk), 2)

def _simulate_chess(bits: list[int], plies: int = 100, prioritize_irreversible=True) -> chess.Board:
    board = chess.Board()
    for i in range(plies):
        legal_moves = list(board.legal_moves)
        if not legal_moves:
            break

        # --- Prioritize irreversible moves (captures, promotions, castling loss) ---
        irreversible = []
        for move in legal_moves:
            if board.is_capture(move) or board.is_en_passant(move) or move.promotion:
                irreversible.append(move)
            elif board.is_castling(move):
                irreversible.append(move)

        use_irreversible = (prioritize_irreversible and (i % 10 < 7))  # 70% of the time

        move_pool = irreversible if use_irreversible and irreversible else legal_moves
        val = _get_chunk_val(bits, i)
        chosen = move_pool[val % len(move_pool)]
        board.push(chosen)
    return board

def _board_to_master_key(board: chess.Board) -> bytes:
    bits = []

    # 1. Occupied squares: 64-bit map
    bits.extend([1 if board.piece_at(i) else 0 for i in chess.SQUARES])

    # 2. Encode each piece (type + color)
    for sq in chess.SQUARES:
        piece = board.piece_at(sq)
        if piece:
            color_bit = 0 if piece.color == chess.WHITE else 1
            type_code = piece.piece_type  # 1–6
            val = (color_bit << 3) | (type_code & 0b111)
            bits.extend([(val >> b) & 1 for b in reversed(range(4))])

    # 3. Turn (1 bit)
    bits.append(0 if board.turn == chess.WHITE else 1)

    # 4. Castling rights (4 bits)
    bits += [int(board.has_kingside_castling_rights(c)) for c in [chess.WHITE, chess.BLACK]]
    bits += [int(board.has_queenside_castling_rights(c)) for c in [chess.WHITE, chess.BLACK]]

    # 5. En passant square (6 bits)
    ep = board.ep_square if board.ep_square is not None else 0
    bits.extend([(ep >> b) & 1 for b in reversed(range(6))])

    # 6. Halfmove clock (7 bits)
    hmc = min(board.halfmove_clock, 127)
    bits.extend([(hmc >> b) & 1 for b in reversed(range(7))])

    # Pad to 256 bits
    while len(bits) < 256:
        bits.extend(bits[:256 - len(bits)])

    return bytes(int(''.join(str(b) for b in bits[i:i+8]), 2) for i in range(0, 256, 8))

# === Public API ===

def derive_master_key(pgn: str, salt: bytes = b'', plies: int = 100) -> bytes:
    board = chess.Board()
    bits = []

    for token in pgn.replace('\n', ' ').split():
        token = token.strip()
        if not token or token.endswith('.'):
            continue
        try:
            move = board.parse_san(token)
            board.push(move)
            uci = move.uci()
            coords = [ord(uci[0]) - ord('a'), ord(uci[1]) - ord('1'),
                      ord(uci[2]) - ord('a'), ord(uci[3]) - ord('1')]
            for c in coords:
                bits.extend([(c >> b) & 1 for b in reversed(range(3))])
        except ValueError:
            continue

    if not bits:
        bits = _password_to_bits(pgn)
    if salt:
        bits += _password_to_bits("", salt)

    final_board = _simulate_chess(bits, plies)
    return _board_to_master_key(final_board)

def derive_master_key_from_password(password: str, salt: bytes = b'', plies: int = 100) -> bytes:
    bits = _password_to_bits(password, salt)
    final_board = _simulate_chess(bits, plies)
    return _board_to_master_key(final_board)
