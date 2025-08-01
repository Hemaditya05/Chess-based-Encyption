#!/usr/bin/env python3
"""
Avalanche test for ChessPerm key derivation.
Tests how small changes in input affect the output.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from chessperm import derive_master_key
import random
from chess import Board

def generate_similar_pgns(base_pgn, num_variations=100):
    """Generate PGNs similar to the base PGN with small variations."""
    variations = []
    
    # Parse the base game
    base_game = Board()
    base_game.set_pgn(base_pgn)
    
    # Generate variations by changing one move
    for _ in range(num_variations):
        game = Board()
        game.set_pgn(base_pgn)
        
        # Make a small change (e.g., change one move)
        legal_moves = list(game.legal_moves)
        if legal_moves:
            # Undo last move if possible
            if len(game.move_stack) > 0:
                game.pop()
            
            # Make a different move
            if legal_moves:
                new_move = random.choice(legal_moves)
                game.push(new_move)
        
        variations.append(game.pgn())
    
    return variations

def avalanche_test():
    """Test avalanche effect in key derivation."""
    print("Running avalanche test...")
    
    # Test with similar PGNs
    base_pgn = "1. e4 e5 2. Nf3 Nc6 3. Bb5 a6 4. Ba4 Nf6"
    variations = generate_similar_pgns(base_pgn, 50)
    
    base_key = derive_master_key(base_pgn)
    total_diff_bits = 0
    total_tests = 0
    
    print(f"Base PGN: {base_pgn}")
    print(f"Base key (first 32 bytes): {base_key[:32].hex()}")
    print("\nTesting variations...")
    
    for i, variation in enumerate(variations):
        try:
            var_key = derive_master_key(variation)
            
            # Calculate bit difference
            diff_bits = sum(bin(b1 ^ b2).count("1") for b1, b2 in zip(base_key, var_key))
            total_diff_bits += diff_bits
            total_tests += 1
            
            print(f"Variation {i+1}: {diff_bits} bits different")
            
        except Exception as e:
            print(f"Error processing variation {i+1}: {e}")
            continue
    
    if total_tests > 0:
        avg_diff = total_diff_bits / total_tests
        print(f"\nAvalanche Test Results:")
        print(f"Average bit difference: {avg_diff:.2f} bits")
        print(f"Expected for random: ~128 bits (50%)")
        print(f"Percentage of bits changed: {avg_diff/256*100:.2f}%")
        
        # Evaluate avalanche quality
        if 110 <= avg_diff <= 146:  # Within 15% of 50%
            print("✓ Good avalanche effect")
        else:
            print("✗ Poor avalanche effect")

def single_bit_avalanche_test():
    """Test avalanche effect with single bit changes in PGN."""
    print("\nRunning single-bit avalanche test...")
    
    # Create a test PGN
    test_pgn = "1. e4 e5 2. Nf3 Nc6 3. Bb5 a6 4. Ba4 Nf6 5. O-O Be7"
    base_key = derive_master_key(test_pgn)
    
    # Test with single character changes
    pgn_bytes = test_pgn.encode('utf-8')
    total_diff_bits = 0
    total_tests = 0
    
    for i in range(len(pgn_bytes)):
        # Flip one bit
        modified_bytes = bytearray(pgn_bytes)
        modified_bytes[i] ^= 1
        
        try:
            modified_pgn = modified_bytes.decode('utf-8', errors='ignore')
            modified_key = derive_master_key(modified_pgn)
            
            # Calculate bit difference
            diff_bits = sum(bin(b1 ^ b2).count("1") for b1, b2 in zip(base_key, modified_key))
            total_diff_bits += diff_bits
            total_tests += 1
            
        except Exception:
            continue
    
    if total_tests > 0:
        avg_diff = total_diff_bits / total_tests
        print(f"Single-bit avalanche test:")
        print(f"Average bit difference per single-bit change: {avg_diff:.2f} bits")
        print(f"Percentage of bits changed: {avg_diff/256*100:.2f}%")

if __name__ == "__main__":
    avalanche_test()
    single_bit_avalanche_test() 