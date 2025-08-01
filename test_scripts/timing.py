#!/usr/bin/env python3
"""
Timing analysis for ChessPerm key derivation.
Checks for timing side-channels.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from chessperm import derive_master_key
import time
import random
import statistics
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

def timing_analysis(num_tests=100):
    """Analyze timing characteristics of key derivation."""
    print(f"Running timing analysis with {num_tests} tests...")
    
    pgns = generate_random_pgns(num_tests, depth=12)
    timings = []
    
    for i, pgn in enumerate(pgns):
        try:
            start_time = time.perf_counter()
            derive_master_key(pgn)
            end_time = time.perf_counter()
            
            duration_ms = (end_time - start_time) * 1000
            timings.append(duration_ms)
            
            if i % 10 == 0:
                print(f"Test {i+1}/{num_tests}: {duration_ms:.3f} ms")
                
        except Exception as e:
            print(f"Error in test {i+1}: {e}")
            continue
    
    if timings:
        print(f"\nTiming Analysis Results:")
        print(f"Number of successful tests: {len(timings)}")
        print(f"Mean time: {statistics.mean(timings):.3f} ms")
        print(f"Median time: {statistics.median(timings):.3f} ms")
        print(f"Standard deviation: {statistics.stdev(timings):.3f} ms")
        print(f"Min time: {min(timings):.3f} ms")
        print(f"Max time: {max(timings):.3f} ms")
        print(f"Range: {max(timings) - min(timings):.3f} ms")
        
        # Check for timing consistency
        cv = statistics.stdev(timings) / statistics.mean(timings)  # Coefficient of variation
        print(f"Coefficient of variation: {cv:.3f}")
        
        if cv < 0.1:
            print("✓ Good timing consistency (low variation)")
        elif cv < 0.2:
            print("⚠ Moderate timing variation")
        else:
            print("✗ High timing variation (potential side-channel)")

def password_timing_analysis(num_tests=100):
    """Analyze timing for password-based key derivation."""
    print(f"\nRunning password timing analysis with {num_tests} tests...")
    
    password_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*"
    timings = []
    
    for i in range(num_tests):
        # Generate random password
        password_length = random.randint(8, 16)
        password = ''.join(random.choice(password_chars) for _ in range(password_length))
        
        try:
            start_time = time.perf_counter()
            derive_master_key(password)
            end_time = time.perf_counter()
            
            duration_ms = (end_time - start_time) * 1000
            timings.append(duration_ms)
            
            if i % 10 == 0:
                print(f"Test {i+1}/{num_tests}: {duration_ms:.3f} ms")
                
        except Exception as e:
            print(f"Error in test {i+1}: {e}")
            continue
    
    if timings:
        print(f"\nPassword Timing Analysis Results:")
        print(f"Number of successful tests: {len(timings)}")
        print(f"Mean time: {statistics.mean(timings):.3f} ms")
        print(f"Median time: {statistics.median(timings):.3f} ms")
        print(f"Standard deviation: {statistics.stdev(timings):.3f} ms")
        print(f"Min time: {min(timings):.3f} ms")
        print(f"Max time: {max(timings):.3f} ms")
        print(f"Range: {max(timings) - min(timings):.3f} ms")
        
        cv = statistics.stdev(timings) / statistics.mean(timings)
        print(f"Coefficient of variation: {cv:.3f}")
        
        if cv < 0.1:
            print("✓ Good timing consistency (low variation)")
        elif cv < 0.2:
            print("⚠ Moderate timing variation")
        else:
            print("✗ High timing variation (potential side-channel)")

def input_length_timing_test():
    """Test if timing varies with input length."""
    print(f"\nTesting timing vs input length...")
    
    # Test with different PGN lengths
    base_pgn = "1. e4 e5 2. Nf3 Nc6 3. Bb5 a6 4. Ba4 Nf6 5. O-O Be7 6. Re1 b5 7. Bb3 d6 8. c3 O-O 9. h3 Nb8 10. d4 Nbd7"
    
    lengths = []
    timings = []
    
    for i in range(1, 21):  # Test PGNs of different lengths
        test_pgn = base_pgn[:i*10]  # Take first i*10 characters
        
        try:
            start_time = time.perf_counter()
            derive_master_key(test_pgn)
            end_time = time.perf_counter()
            
            duration_ms = (end_time - start_time) * 1000
            lengths.append(len(test_pgn))
            timings.append(duration_ms)
            
            print(f"Length {len(test_pgn)}: {duration_ms:.3f} ms")
            
        except Exception as e:
            print(f"Error with length {len(test_pgn)}: {e}")
            continue
    
    if lengths and timings:
        # Calculate correlation
        import numpy as np
        correlation = np.corrcoef(lengths, timings)[0, 1]
        print(f"\nCorrelation between input length and timing: {correlation:.3f}")
        
        if abs(correlation) < 0.3:
            print("✓ Good: Low correlation between input length and timing")
        elif abs(correlation) < 0.7:
            print("⚠ Moderate: Some correlation between input length and timing")
        else:
            print("✗ Poor: High correlation between input length and timing (side-channel risk)")

if __name__ == "__main__":
    # PGN timing analysis
    timing_analysis(100)
    
    # Password timing analysis
    password_timing_analysis(100)
    
    # Input length timing test
    input_length_timing_test() 