#!/usr/bin/env python3
"""
Collision test for ChessPerm key derivation.
Tests for hash collisions in derived master keys.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from chessperm import derive_master_key
import hashlib
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

def collision_test(n=10000):
    """Test for collisions in derived master keys."""
    print(f"Running collision test with {n} PGNs...")
    
    seen = set()
    collisions = 0
    
    for i, pgn in enumerate(generate_random_pgns(n, depth=12)):
        if i % 1000 == 0:
            print(f"Processed {i}/{n} PGNs...")
        
        try:
            k = derive_master_key(pgn)
            h = hashlib.sha256(k).hexdigest()
            
            if h in seen:
                collisions += 1
                print(f"COLLISION FOUND! PGN: {pgn[:100]}...")
            else:
                seen.add(h)
        except Exception as e:
            print(f"Error processing PGN: {e}")
            continue
    
    print(f"\nCollision Test Results:")
    print(f"Tested {n} PGNs")
    print(f"Collisions found: {collisions}")
    print(f"Collision rate: {collisions/n*100:.4f}%")
    print(f"Unique hashes: {len(seen)}")
    
    return collisions

if __name__ == "__main__":
    collision_test() 