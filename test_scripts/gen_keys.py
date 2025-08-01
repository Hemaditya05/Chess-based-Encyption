#!/usr/bin/env python3
"""
Generate a large sample of keys for randomness testing.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from chessperm import derive_master_key
import random
from chess import Board

def generate_random_pgns(n, depth=12):
    """Generate n random PGN strings with specified depth."""
    pgns = []
    for _ in range(n):
        # Create a random chess game
        game = Board()
        moves = []
        
        # Generate random moves up to depth
        for i in range(depth):
            legal_moves = list(game.legal_moves)
            if not legal_moves:
                break
            move = random.choice(legal_moves)
            game.push(move)
            moves.append(game.san(move))
        
        pgn = game.pgn()
        if pgn.strip():
            pgns.append(pgn)
    
    return pgns

def generate_key_sample(num_keys=50000, output_file="keys.bin"):
    """Generate a large sample of keys for randomness testing."""
    print(f"Generating {num_keys} keys for randomness testing...")
    
    keys = b''
    pgns = generate_random_pgns(num_keys, depth=12)
    
    for i, pgn in enumerate(pgns):
        if i % 1000 == 0:
            print(f"Generated {i}/{num_keys} keys...")
        
        try:
            key = derive_master_key(pgn)
            keys += key
        except Exception as e:
            print(f"Error generating key for PGN {i}: {e}")
            continue
    
    # Write to binary file
    with open(output_file, "wb") as f:
        f.write(keys)
    
    print(f"Generated {len(keys)} bytes of key data")
    print(f"Saved to {output_file}")
    print(f"Number of complete keys: {len(keys) // 32}")
    
    return output_file

def generate_password_keys(num_keys=10000, output_file="password_keys.bin"):
    """Generate keys from random passwords for testing."""
    print(f"Generating {num_keys} password-based keys...")
    
    keys = b''
    
    # Generate random passwords
    password_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*"
    
    for i in range(num_keys):
        if i % 1000 == 0:
            print(f"Generated {i}/{num_keys} password keys...")
        
        # Generate random password
        password_length = random.randint(8, 16)
        password = ''.join(random.choice(password_chars) for _ in range(password_length))
        
        try:
            key = derive_master_key(password)
            keys += key
        except Exception as e:
            print(f"Error generating key for password {i}: {e}")
            continue
    
    # Write to binary file
    with open(output_file, "wb") as f:
        f.write(keys)
    
    print(f"Generated {len(keys)} bytes of password key data")
    print(f"Saved to {output_file}")
    print(f"Number of complete keys: {len(keys) // 32}")
    
    return output_file

if __name__ == "__main__":
    # Generate PGN-based keys
    generate_key_sample(50000, "pgn_keys.bin")
    
    # Generate password-based keys
    generate_password_keys(10000, "password_keys.bin")
    
    print("\nKey generation complete!")
    print("Files created:")
    print("- pgn_keys.bin: 50,000 PGN-based keys")
    print("- password_keys.bin: 10,000 password-based keys")
    print("\nYou can now run randomness tests on these files.") 