# Copyright (C) 2025 unelected
#
# This file is part of the zafiaonline project.
#
# This program is free software: you can redistribute it and/or modify it under the terms of the
# GNU Lesser General Public License as published by the Free Software Foundation, either version 3
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License along with this program.
# If not, see <https://www.gnu.org/licenses/>.

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
