from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError, InvalidHash

class PasswordService:
    """Secure password hashing using Argon2."""
    
    def __init__(self):
        self.ph = PasswordHasher(
            time_cost=2,
            memory_cost=65536,
            parallelism=4,
            hash_len=32,
            salt_len=16
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
            return False
        except (VerificationError, InvalidHash) as e:
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


password_service = PasswordService()


def hash_password(password: str) -> str:
    """Hash a password."""
    return password_service.hash_password(password)