#!/usr/bin/env python3
"""
Differential propagation test for ChessPerm key derivation.
Analyzes how single-bit changes propagate through the system.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from chessperm import derive_master_key
import random

def test_single_bit_propagation():
    """Test how single-bit changes propagate through key derivation."""
    print("Testing single-bit propagation...")
    
    # Test with different input types
    test_inputs = [
        "1. e4 e5 2. Nf3 Nc6 3. Bb5 a6 4. Ba4 Nf6",
        "password123",
        "This is a test message for differential analysis",
        "♔♕♖♗♘♙♚♛♜♝♞♟"
    ]
    
    for test_input in test_inputs:
        print(f"\nTesting input: {test_input[:50]}...")
        
        # Convert to bytes
        input_bytes = test_input.encode('utf-8')
        base_key = derive_master_key(test_input)
        
        total_diff_bits = 0
        total_tests = 0
        
        # Test single-bit changes
        for i in range(len(input_bytes)):
            # Create modified input with one bit flipped
            modified_bytes = bytearray(input_bytes)
            modified_bytes[i] ^= 1
            
            try:
                modified_input = modified_bytes.decode('utf-8', errors='ignore')
                modified_key = derive_master_key(modified_input)
                
                # Calculate bit difference
                diff_bits = sum(bin(b1 ^ b2).count("1") for b1, b2 in zip(base_key, modified_key))
                total_diff_bits += diff_bits
                total_tests += 1
                
            except Exception as e:
                print(f"Error with bit flip at position {i}: {e}")
                continue
        
        if total_tests > 0:
            avg_diff = total_diff_bits / total_tests
            print(f"Average bit difference per single-bit change: {avg_diff:.2f} bits")
            print(f"Percentage of bits changed: {avg_diff/256*100:.2f}%")
            
            # Evaluate propagation quality
            if 110 <= avg_diff <= 146:  # Within 15% of 50%
                print("✓ Good differential propagation")
            else:
                print("✗ Poor differential propagation")

def test_avalanche_effect():
    """Test avalanche effect with different input modifications."""
    print("\nTesting avalanche effect...")
    
    base_pgn = "1. e4 e5 2. Nf3 Nc6 3. Bb5 a6 4. Ba4 Nf6"
    base_key = derive_master_key(base_pgn)
    
    # Test different types of modifications
    modifications = [
        ("1. e4 e5 2. Nf3 Nc6 3. Bb5 a6 4. Bc4 Nf6", "Changed Bb5 to Bc4"),
        ("1. e4 e5 2. Nf3 Nc6 3. Bb5 a6 4. Ba4 Nf6 5. O-O", "Added one move"),
        ("1. e4 e5 2. Nf3 Nc6 3. Bb5 a6 4. Ba4", "Removed one move"),
        ("1. e4 e5 2. Nf3 Nc6 3. Bb5 a6 4. Ba4 Nf6 ", "Added space"),
        ("1.e4 e5 2.Nf3 Nc6 3.Bb5 a6 4.Ba4 Nf6", "Removed spaces"),
    ]
    
    print(f"Base PGN: {base_pgn}")
    print(f"Base key (first 32 bytes): {base_key[:32].hex()}")
    print("\nTesting modifications:")
    
    for modified_pgn, description in modifications:
        try:
            modified_key = derive_master_key(modified_pgn)
            diff_bits = sum(bin(b1 ^ b2).count("1") for b1, b2 in zip(base_key, modified_key))
            
            print(f"{description}: {diff_bits} bits different ({diff_bits/256*100:.1f}%)")
            
        except Exception as e:
            print(f"Error with modification '{description}': {e}")

def test_password_differential():
    """Test differential propagation with passwords."""
    print("\nTesting password differential propagation...")
    
    base_password = "mypassword123"
    base_key = derive_master_key(base_password)
    
    # Test different password modifications
    modifications = [
        ("mypassword124", "Changed last digit"),
        ("mypassword12", "Removed last character"),
        ("mypassword1234", "Added one character"),
        ("mypassword123 ", "Added space"),
        ("mypassword12!", "Changed last character"),
        ("mypassword123", "Same password (control)"),
    ]
    
    print(f"Base password: {base_password}")
    print(f"Base key (first 32 bytes): {base_key[:32].hex()}")
    print("\nTesting password modifications:")
    
    for modified_password, description in modifications:
        try:
            modified_key = derive_master_key(modified_password)
            diff_bits = sum(bin(b1 ^ b2).count("1") for b1, b2 in zip(base_key, modified_key))
            
            print(f"{description}: {diff_bits} bits different ({diff_bits/256*100:.1f}%)")
            
        except Exception as e:
            print(f"Error with modification '{description}': {e}")

def test_unicode_differential():
    """Test differential propagation with Unicode characters."""
    print("\nTesting Unicode differential propagation...")
    
    base_input = "♔♕♖♗♘♙♚♛♜♝♞♟"
    base_key = derive_master_key(base_input)
    
    # Test Unicode modifications
    modifications = [
        ("♔♕♖♗♘♙♚♛♜♝♞", "Removed one character"),
        ("♔♕♖♗♘♙♚♛♜♝♞♟♠", "Added one character"),
        ("♔♕♖♗♘♙♚♛♜♝♞♟ ", "Added space"),
        ("♔♕♖♗♘♙♚♛♜♝♞♟♔", "Changed last character"),
    ]
    
    print(f"Base input: {base_input}")
    print(f"Base key (first 32 bytes): {base_key[:32].hex()}")
    print("\nTesting Unicode modifications:")
    
    for modified_input, description in modifications:
        try:
            modified_key = derive_master_key(modified_input)
            diff_bits = sum(bin(b1 ^ b2).count("1") for b1, b2 in zip(base_key, modified_key))
            
            print(f"{description}: {diff_bits} bits different ({diff_bits/256*100:.1f}%)")
            
        except Exception as e:
            print(f"Error with modification '{description}': {e}")

if __name__ == "__main__":
    # Test single-bit propagation
    test_single_bit_propagation()
    
    # Test avalanche effect
    test_avalanche_effect()
    
    # Test password differential
    test_password_differential()
    
    # Test Unicode differential
    test_unicode_differential()
    
    print("\nDifferential propagation analysis complete!") 