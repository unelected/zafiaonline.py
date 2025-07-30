"""
Utilities for MD5 hashing.

This module provides a static utility class `Md5` that includes methods
for computing MD5 hashes, with and without repeated salting.

Typical usage involves hashing sensitive strings such as passwords or tokens
in a way compatible with the Mafia protocol (which requires a specific salt
and number of iterations).
"""
import hashlib

class Md5:
    """
    Utility class for performing MD5-based hashing.

    This class provides static functionality for computing raw and salted
    MD5 hashes. It is stateless and does not define any instance attributes.
    """
    @staticmethod
    def md5_hash(string: str) -> str:
        """
        Returns the MD5 hash of the given string.

        Args:
            string (str): The input string to hash.

        Returns:
            str: The MD5 hash of the input string.
        """
        return hashlib.md5(string.encode()).hexdigest()

    @staticmethod
    def md5salt(string: str, salt: str = "azxsw", iterations: int = 5) -> str:
        """
        Returns a string hashed multiple times with a salt.

        Args:
            string (str): The input string to hash.
            salt (str, optional): The salt to append before hashing. Defaults to "azxsw".
            iterations (int, optional): Number of hash iterations. Defaults to 5.

        Returns:
            str: The salted and repeatedly hashed string.
        """
        for _ in range(iterations):
            string = Md5.md5_hash(string + salt)
        return string
