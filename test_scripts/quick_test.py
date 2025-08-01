#!/usr/bin/env python3
"""
Quick test to verify the test suite works.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from chessperm import derive_master_key
import hashlib
import random
from chess import Board

def quick_collision_test(n=100):
    """Quick collision test with smaller sample."""
    print(f"Quick collision test with {n} PGNs...")
    
    seen = set()
    collisions = 0
    
    for i in range(n):
        # Create a simple test PGN
        game = Board()
        moves = []
        
        # Make a few random moves
        for _ in range(6):
            legal_moves = list(game.legal_moves)
            if not legal_moves:
                break
            move = random.choice(legal_moves)
            game.push(move)
        
        pgn = game.pgn()
        if pgn.strip():
            try:
                k = derive_master_key(pgn)
                h = hashlib.sha256(k).hexdigest()
                
                if h in seen:
                    collisions += 1
                    print(f"COLLISION FOUND! PGN: {pgn[:50]}...")
                else:
                    seen.add(h)
                    
                if i % 10 == 0:
                    print(f"Processed {i+1}/{n} PGNs...")
                    
            except Exception as e:
                print(f"Error processing PGN: {e}")
                continue
    
    print(f"\nQuick Test Results:")
    print(f"Tested {n} PGNs")
    print(f"Collisions found: {collisions}")
    print(f"Collision rate: {collisions/n*100:.4f}%")
    print(f"Unique hashes: {len(seen)}")
    
    return collisions

if __name__ == "__main__":
    quick_collision_test(50) 