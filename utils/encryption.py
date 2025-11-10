"""
Windows DPAPI encryption utilities for secure credential storage.
"""
import base64
import platform


def encrypt_string(plaintext: str) -> str:
    """
    Encrypt a string using Windows DPAPI.
    Returns base64 encoded encrypted data prefixed with 'dpapi:'.
    
    Args:
        plaintext: The string to encrypt
        
    Returns:
        Encrypted string in format 'dpapi:base64data'
    """
    if platform.system() != 'Windows':
        # Fallback for non-Windows (development on Mac/Linux)
        return f"plain:{plaintext}"
    
    try:
        import win32crypt
        
        # Encrypt with DPAPI
        encrypted_bytes = win32crypt.CryptProtectData(
            plaintext.encode('utf-8'),
            None,  # Optional description
            None,  # Optional entropy
            None,  # Reserved
            None,  # Prompt struct
            0      # Flags
        )
        
        # Encode to base64 for JSON storage
        encoded = base64.b64encode(encrypted_bytes).decode('ascii')
        return f"dpapi:{encoded}"
        
    except ImportError:
        # pywin32 not available, fallback to plaintext with warning
        print("WARNING: pywin32 not available, storing credentials in plaintext")
        return f"plain:{plaintext}"
    except Exception as e:
        print(f"WARNING: Encryption failed ({e}), storing in plaintext")
        return f"plain:{plaintext}"


def decrypt_string(encrypted: str) -> str:
    """
    Decrypt a string encrypted with Windows DPAPI.
    
    Args:
        encrypted: Encrypted string in format 'dpapi:base64data' or 'plain:data'
        
    Returns:
        Decrypted plaintext string
    """
    if not encrypted:
        return ""
    
    # Check if it's a plaintext fallback
    if encrypted.startswith("plain:"):
        return encrypted[6:]  # Remove 'plain:' prefix
    
    # Check if it's encrypted
    if not encrypted.startswith("dpapi:"):
        # Legacy plaintext value (no prefix)
        return encrypted
    
    if platform.system() != 'Windows':
        raise Exception("DPAPI encrypted data can only be decrypted on Windows")
    
    try:
        import win32crypt
        
        # Remove 'dpapi:' prefix and decode base64
        encoded = encrypted[6:]
        encrypted_bytes = base64.b64decode(encoded)
        
        # Decrypt with DPAPI
        _, decrypted_bytes = win32crypt.CryptUnprotectData(
            encrypted_bytes,
            None,  # Optional entropy
            None,  # Reserved
            None,  # Prompt struct
            0      # Flags
        )
        
        return decrypted_bytes.decode('utf-8')
        
    except ImportError:
        raise Exception("pywin32 not available, cannot decrypt")
    except Exception as e:
        raise Exception(f"Decryption failed: {e}")


def is_encrypted(value: str) -> bool:
    """
    Check if a string is encrypted with DPAPI.
    
    Args:
        value: String to check
        
    Returns:
        True if encrypted, False otherwise
    """
    return isinstance(value, str) and value.startswith("dpapi:")
