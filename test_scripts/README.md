# ChessPerm Security Test Suite

This directory contains comprehensive security testing scripts for the ChessPerm key derivation function.

## Setup

1. **Create Virtual Environment**:
   ```bash
   python -m venv chessperm_test_env
   source chessperm_test_env/bin/activate  # Linux/Mac
   # or
   chessperm_test_env\Scripts\activate     # Windows
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Optional External Tools** (for advanced testing):
   - **Dieharder**: `sudo apt-get install dieharder` (Ubuntu/Debian)
   - **NIST STS**: Download from NIST website
   - **Hashcat**: `sudo apt-get install hashcat` (Ubuntu/Debian)

## Test Scripts

### 1. Collision Test (`collision_test.py`)
Tests for hash collisions in derived master keys.

```bash
python collision_test.py
```

**What it tests**:
- Generates 10,000 random PGNs
- Derives master keys for each
- Checks for SHA-256 hash collisions
- Reports collision rate and statistics

### 2. Avalanche Test (`avalanche_test.py`)
Tests the avalanche effect - how small changes in input affect output.

```bash
python avalanche_test.py
```

**What it tests**:
- Single-bit changes in input
- PGN variations (move changes, additions, removals)
- Measures bit difference between outputs
- Evaluates avalanche quality (should be ~50% bit difference)

### 3. Timing Analysis (`timing.py`)
Checks for timing side-channels in the key derivation function.

```bash
python timing.py
```

**What it tests**:
- Timing consistency across different inputs
- Correlation between input length and timing
- Coefficient of variation analysis
- Side-channel resistance evaluation

### 4. Differential Propagation (`diff_probe.py`)
Analyzes how single-bit changes propagate through the system.

```bash
python diff_probe.py
```

**What it tests**:
- Single-bit input modifications
- Unicode character handling
- Password vs PGN input differences
- Differential propagation quality

### 5. Performance Benchmark (`bench.py`)
Benchmarks throughput and performance characteristics.

```bash
python bench.py
```

**What it tests**:
- Key derivation throughput (derivations/sec)
- Memory usage patterns
- Performance comparison: PGN vs Password modes
- Resource utilization analysis

### 6. Key Generation (`gen_keys.py`)
Generates large key samples for external randomness testing.

```bash
python gen_keys.py
```

**Output files**:
- `pgn_keys.bin`: 50,000 PGN-based keys
- `password_keys.bin`: 10,000 password-based keys

## Comprehensive Test Runner

Run all tests at once with the comprehensive test runner:

```bash
python run_all_tests.py
```

This will:
1. Execute all security tests
2. Generate a detailed report
3. Save results to timestamped report file
4. Provide summary statistics

## External Randomness Testing

After generating key files with `gen_keys.py`, you can use external tools:

### NIST Statistical Test Suite
```bash
niststs --input pgn_keys.bin --blocksize 32
```

### Dieharder
```bash
dieharder -a -g 202 -f pgn_keys.bin
```

### Hashcat (for brute-force simulation)
```bash
# Create a target hash
echo -n "hashed_key_here" > target.txt

# Attack with hashcat
hashcat -a 3 -m 8900 target.txt ?l?l?l?l?l?l?l?l
```

## Expected Results

### Good Security Indicators:
- **Collision Rate**: < 0.01% (very low collision rate)
- **Avalanche Effect**: ~50% bit difference (110-146 bits out of 256)
- **Timing Consistency**: Coefficient of variation < 0.1
- **Differential Propagation**: ~50% bit difference per single-bit change
- **Performance**: > 1000 derivations/sec

### Warning Signs:
- High collision rates (> 0.1%)
- Poor avalanche effect (< 30% or > 70% bit difference)
- High timing variation (CV > 0.2)
- Poor differential propagation
- Performance issues (< 100 derivations/sec)

## Test Categories

### 1. Cryptographic Strength
- Collision resistance
- Avalanche effect
- Differential propagation

### 2. Side-Channel Resistance
- Timing analysis
- Memory usage patterns
- Input length correlation

### 3. Performance
- Throughput benchmarking
- Resource utilization
- Scalability testing

### 4. Randomness Quality
- Statistical distribution
- Entropy analysis
- External randomness suite compatibility

## Troubleshooting

### Common Issues:

1. **Import Errors**: Make sure backend directory is in Python path
2. **Memory Issues**: Reduce test sizes in scripts for limited RAM
3. **External Tool Errors**: Install required system packages
4. **Performance Issues**: Run on faster hardware or reduce test counts

### Performance Tuning:

- Reduce test counts in scripts for faster execution
- Use smaller key samples for memory-constrained systems
- Run individual tests instead of full suite if needed

## Report Interpretation

The test runner generates a comprehensive report with:

- **Summary Statistics**: Pass/fail rates, timing, success rates
- **Detailed Results**: Individual test outputs and errors
- **Recommendations**: Based on security thresholds
- **Timestamps**: For tracking changes over time

## Contributing

To add new tests:

1. Create new test script following existing patterns
2. Add to `run_all_tests.py` test list
3. Update this README with test description
4. Ensure proper error handling and reporting

## Security Notes

- Tests are designed to be non-destructive
- Generated key files contain random data (not real keys)
- All tests run in isolated environment
- No sensitive data is logged or stored 