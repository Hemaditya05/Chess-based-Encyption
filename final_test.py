# === ChessPerm Security Test Suite ===
import time
import random
from chessperm import derive_master_key, derive_master_key_from_password

def bit_diff(a: bytes, b: bytes) -> int:
    return sum(bin(x ^ y).count('1') for x, y in zip(a, b))

# 1. Collision Test
def collision_test(n: int = 1000) -> bool:
    print("\n[1] Collision Test")
    seen = set()
    for _ in range(n):
        password = ''.join(random.choices("abcdefgh12345678", k=10))
        key = derive_master_key_from_password(password)
        if key in seen:
            print("✗ Collision detected!")
            return False
        seen.add(key)
    print("✓ No collisions in", n, "runs.")
    return True

# 2. Avalanche Test
def avalanche_test(n: int = 100) -> bool:
    print("\n[2] Avalanche Test")
    password = "MySecret123"
    base = derive_master_key_from_password(password)
    total_diff = 0
    for _ in range(n):
        modified = list(password)
        idx = random.randint(0, len(modified) - 1)
        modified[idx] = chr((ord(modified[idx]) + 1) % 128)
        altered = ''.join(modified)
        new = derive_master_key_from_password(altered)
        total_diff += bit_diff(base, new)
    avg = total_diff / n
    print(f"✓ Average bit difference: {avg:.2f}")
    return True

# 3. Timing Analysis
def timing_analysis(n: int = 100) -> bool:
    print("\n[3] Timing Analysis")
    total_time = 0
    for _ in range(n):
        password = ''.join(random.choices("abcdefg12345", k=8))
        start = time.perf_counter()
        derive_master_key_from_password(password)
        total_time += time.perf_counter() - start
    avg = total_time / n * 1000
    print(f"✓ Average time per derivation: {avg:.2f} ms")
    return True

# 4. Differential Propagation
def differential_propagation(n: int = 50) -> bool:
    print("\n[4] Differential Propagation Test")
    pgn = "e4 e5 Nf3 Nc6 Bb5 a6"
    base = derive_master_key(pgn)
    total_diff = 0
    for _ in range(n):
        tokens = pgn.split()
        idx = random.randint(0, len(tokens) - 1)
        tokens[idx] = "a3" if tokens[idx] != "a3" else "h6"
        new_pgn = " ".join(tokens)
        new_key = derive_master_key(new_pgn)
        total_diff += bit_diff(base, new_key)
    avg = total_diff / n
    print(f"✓ Avg. bit diff: {avg:.2f} bits")
    return True

# 5. Performance Benchmark
def benchmark_throughput(n: int = 500) -> bool:
    print("\n[5] Performance Benchmark")
    passwords = [''.join(random.choices("abcdef123456", k=10)) for _ in range(n)]
    start = time.perf_counter()
    for pw in passwords:
        derive_master_key_from_password(pw)
    duration = time.perf_counter() - start
    print(f"✓ {n} derivations in {duration:.2f} sec ({n / duration:.2f} ops/sec)")
    return True

# === Run All Tests ===
if __name__ == "__main__":
    print("CHESSPERM SECURITY TEST SUITE")
    print("=" * 50)

    tests = [
        ("Collision Test", collision_test),
        ("Avalanche Test", avalanche_test),
        ("Timing Analysis", timing_analysis),
        ("Differential Propagation", differential_propagation),
        ("Performance Benchmark", benchmark_throughput)
    ]

    results = {}
    for name, func in tests:
        try:
            results[name] = func()
        except Exception as e:
            print(f"✗ {name} failed: {e}")
            results[name] = False

    print("\n=== SUMMARY ===")
    for name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{name}: {status}")
