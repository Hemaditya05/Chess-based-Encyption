#!/usr/bin/env python3
"""
Simple test to verify ChessPerm functionality.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from chessperm import derive_master_key

def simple_test():
    """Simple test of ChessPerm functionality."""
    print("Testing ChessPerm key derivation...")
    
    # Test with a simple PGN
    test_pgn = "1. e4 e5 2. Nf3 Nc6"
    print(f"Input PGN: {test_pgn}")
    
    try:
        key = derive_master_key(test_pgn)
        print(f"Derived key (first 32 bytes): {key[:32].hex()}")
        print(f"Key length: {len(key)} bytes")
        print("✓ Key derivation successful!")
        
        # Test with password
        test_password = "mypassword123"
        print(f"\nInput password: {test_password}")
        
        key2 = derive_master_key(test_password)
        print(f"Derived key (first 32 bytes): {key2[:32].hex()}")
        print(f"Key length: {len(key2)} bytes")
        print("✓ Password key derivation successful!")
        
        # Test that different inputs produce different keys
        if key != key2:
            print("✓ Different inputs produce different keys")
        else:
            print("✗ Different inputs produced same key (unexpected)")
            
    except Exception as e:
        print(f"✗ Error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = simple_test()
    if success:
        print("\n✓ All tests passed!")
    else:
        print("\n✗ Tests failed!") 