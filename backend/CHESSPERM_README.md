# Enhanced ChessPerm Master Key Derivation

## Overview

This module generates a cryptographic master key from chess games or passwords, using a custom block cipher inspired by chess mechanics. The new robust mode increases security and uniqueness by combining multiple chess and cryptographic features.

## Key Features

- **Chess Context**: Uses not just the move sequence, but also the final board state (FEN), and chess-specific features (piece counts, castling rights, en passant square).
- **Salt & Iterations**: Supports a salt and multiple rounds of mixing, similar to PBKDF2, to resist brute-force attacks.
- **Hashing**: Final output is hashed with SHA-256 for uniformity and avalanche effect.
- **Password Mode**: Passwords are processed with the same robust logic, with optional salt.

## Usage

### Deriving a Key from Chess Game

```python
from chessperm import derive_master_key_robust

key = derive_master_key_robust(
    pgn_string,
    salt=b'some_salt',         # Optional: bytes
    iterations=10000,          # Optional: int, default 1000
)
```

### Deriving a Key from Password

```python
from chessperm import derive_master_key_from_password_robust

key = derive_master_key_from_password_robust(
    password,
    salt=b'some_salt',         # Optional: bytes
    iterations=10000,          # Optional: int, default 1000
)
```

## Security Notes

- Always use a unique, random salt for each encryption session.
- Higher iteration counts increase security but also computation time.
- The key is highly sensitive to all chess and password inputs.

## What’s New

- Board state, FEN, and chess features are now part of the key.
- Salt and iteration count make brute-force attacks much harder.
- Output is hashed for cryptographic strength.