#!/usr/bin/env python3
"""
Benchmark script for ChessPerm key derivation.
Tests throughput and performance characteristics.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from chessperm import derive_master_key
import time
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

def benchmark_throughput(num_tests=1000):
    """Benchmark the throughput of key derivation."""
    print(f"Benchmarking ChessPerm key derivation...")
    print(f"Number of tests: {num_tests}")
    
    # Generate test PGNs
    pgns = generate_random_pgns(num_tests, depth=12)
    
    # Warm up
    print("Warming up...")
    for _ in range(10):
        derive_master_key("1. e4 e5")
    
    # Benchmark
    print("Running benchmark...")
    start_time = time.time()
    
    for i, pgn in enumerate(pgns):
        try:
            derive_master_key(pgn)
            if i % 100 == 0:
                elapsed = time.time() - start_time
                rate = (i + 1) / elapsed
                print(f"Processed {i+1}/{num_tests} - Rate: {rate:.1f} derivations/sec")
        except Exception as e:
            print(f"Error processing PGN {i}: {e}")
            continue
    
    end_time = time.time()
    total_time = end_time - start_time
    
    print(f"\nBenchmark Results:")
    print(f"Total time: {total_time:.2f} seconds")
    print(f"Total derivations: {len(pgns)}")
    print(f"Throughput: {len(pgns)/total_time:.1f} derivations/sec")
    print(f"Average time per derivation: {total_time/len(pgns)*1000:.2f} ms")

def benchmark_password_mode(num_tests=1000):
    """Benchmark password-based key derivation."""
    print(f"\nBenchmarking password-based key derivation...")
    print(f"Number of tests: {num_tests}")
    
    # Generate random passwords
    password_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*"
    passwords = []
    
    for _ in range(num_tests):
        password_length = random.randint(8, 16)
        password = ''.join(random.choice(password_chars) for _ in range(password_length))
        passwords.append(password)
    
    # Warm up
    print("Warming up...")
    for _ in range(10):
        derive_master_key("testpassword123")
    
    # Benchmark
    print("Running benchmark...")
    start_time = time.time()
    
    for i, password in enumerate(passwords):
        try:
            derive_master_key(password)
            if i % 100 == 0:
                elapsed = time.time() - start_time
                rate = (i + 1) / elapsed
                print(f"Processed {i+1}/{num_tests} - Rate: {rate:.1f} derivations/sec")
        except Exception as e:
            print(f"Error processing password {i}: {e}")
            continue
    
    end_time = time.time()
    total_time = end_time - start_time
    
    print(f"\nPassword Benchmark Results:")
    print(f"Total time: {total_time:.2f} seconds")
    print(f"Total derivations: {len(passwords)}")
    print(f"Throughput: {len(passwords)/total_time:.1f} derivations/sec")
    print(f"Average time per derivation: {total_time/len(passwords)*1000:.2f} ms")

def memory_usage_test():
    """Test memory usage during key derivation."""
    print(f"\nTesting memory usage...")
    
    import psutil
    import os
    
    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss / 1024 / 1024  # MB
    
    print(f"Initial memory usage: {initial_memory:.2f} MB")
    
    # Generate many keys
    pgns = generate_random_pgns(1000, depth=12)
    
    for i, pgn in enumerate(pgns):
        derive_master_key(pgn)
        if i % 100 == 0:
            current_memory = process.memory_info().rss / 1024 / 1024
            print(f"After {i+1} derivations: {current_memory:.2f} MB")
    
    final_memory = process.memory_info().rss / 1024 / 1024
    print(f"Final memory usage: {final_memory:.2f} MB")
    print(f"Memory increase: {final_memory - initial_memory:.2f} MB")

if __name__ == "__main__":
    # Benchmark PGN mode
    benchmark_throughput(1000)
    
    # Benchmark password mode
    benchmark_password_mode(1000)
    
    # Memory usage test (if psutil is available)
    try:
        import psutil
        memory_usage_test()
    except ImportError:
        print("\nSkipping memory usage test (psutil not available)")
        print("Install with: pip install psutil") 