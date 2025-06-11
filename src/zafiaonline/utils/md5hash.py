import hashlib

class Md5:
    @staticmethod
    def md5_hash(string: str) -> str:
        """
        Returns the MD5 hash of a string.

        :param string: The input string to hash.
        :return: The MD5 hash of the input string.
        """
        return hashlib.md5(string.encode()).hexdigest()

    @staticmethod
    def md5salt(string: str, salt: str = "azxsw", iterations: int = 5) -> str:
        """
        Returns a string hashed multiple times with a salt.

        :param string: The input string to hash.
        :param salt: The salt to append to the string before hashing (Mafia
        requires "azxsw").
        :param iterations: The number of times to hash the string (Mafia
        requires 5).
        :return: The salted and hashed string.
        """
        for _ in range(iterations):
            string = Md5.md5_hash(string + salt)
        return string