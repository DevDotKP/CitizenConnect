
import os
# Mock missing env
if "ENCRYPTION_KEY" in os.environ:
    del os.environ["ENCRYPTION_KEY"]

try:
    from security_utils import get_secret
    
    # Case 1: Value looks encrypted but no key
    os.environ["TEST_SECRET"] = "gAAAAABl..." 
    val = get_secret("TEST_SECRET")
    print(f"Case 1 (Encrypted, No Key): {val}")
    
    # Case 2: Value is plaintext
    os.environ["TEST_PLAIN"] = "plaintext"
    val = get_secret("TEST_PLAIN")
    print(f"Case 2 (Plaintext): {val}")
    
except Exception as e:
    print(f"Crashed: {e}")
