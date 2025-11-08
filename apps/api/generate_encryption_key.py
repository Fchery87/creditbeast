#!/usr/bin/env python3
"""
Generate a Fernet encryption key for PII_ENCRYPTION_KEY environment variable

Run this script to generate a new encryption key:
    python generate_encryption_key.py

Then add the output to your .env file as:
    PII_ENCRYPTION_KEY=<generated_key>

WARNING: Keep this key secret! If you lose it, encrypted data cannot be recovered.
"""

from cryptography.fernet import Fernet

# Generate a new Fernet key
key = Fernet.generate_key()

print("=" * 70)
print("Generated Fernet Encryption Key")
print("=" * 70)
print()
print("Add this to your .env file:")
print()
print(f"PII_ENCRYPTION_KEY={key.decode()}")
print()
print("=" * 70)
print("IMPORTANT:")
print("- Keep this key secret and secure")
print("- Never commit this key to version control")
print("- If you lose this key, encrypted PII data cannot be recovered")
print("- Use the same key across all environments for the same database")
print("=" * 70)
