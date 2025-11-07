from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError, InvalidHash

class PasswordService:
    """Secure password hashing using Argon2."""
    
    def __init__(self):
        # Configure Argon2 parameters
        # These are secure defaults, but you can adjust based on your needs
        self.ph = PasswordHasher(
            time_cost=2,        # Number of iterations
            memory_cost=65536,  # Memory usage in KiB (64 MB)
            parallelism=4,      # Number of parallel threads
            hash_len=32,        # Length of hash in bytes
            salt_len=16         # Length of random salt in bytes
        )
    
    def hash_password(self, password: str) -> str:
        """
        Hash a password using Argon2.
        Salt is automatically generated and included in the hash.
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password string (includes salt and parameters)
        """
        if not password:
            raise ValueError("Password cannot be empty")
        
        return self.ph.hash(password)
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """
        Verify a password against its hash.
        
        Args:
            password: Plain text password to verify
            hashed: Previously hashed password
            
        Returns:
            True if password matches, False otherwise
        """
        try:
            self.ph.verify(hashed, password)
            return True
        except VerifyMismatchError:
            # Password doesn't match
            return False
        except (VerificationError, InvalidHash) as e:
            # Invalid hash format or other verification error
            print(f"Password verification error: {e}")
            return False
    
    def needs_rehash(self, hashed: str) -> bool:
        """
        Check if a hash needs to be rehashed with updated parameters.
        Useful if you change security parameters over time.
        """
        try:
            return self.ph.check_needs_rehash(hashed)
        except (InvalidHash, Exception):
            return True


# Create a singleton instance
password_service = PasswordService()


def hash_password(password: str) -> str:
    """Hash a password."""
    return password_service.hash_password(password)