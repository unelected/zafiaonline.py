# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2025 unelected
#
# This file is part of the zafiaonline project.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
Proxy store module.

This module provides the ProxyStore class for managing proxies
in memory, as well as a global `store` instance that can be
imported and used across the project.

Example:
    from zafiaonline.proxy_store import store
    store.add("http://1.2.3.4:8080")
    proxy = store.get_random_proxy()
"""
from zafiaonline.utils.logging_config import logger


class ProxyStore:
    """
    In-memory storage for proxies.

    This class provides methods to add, retrieve, and
    fetch random proxies. Proxies are stored only in
    memory and will be lost after program termination.
    """
    def __init__(self) -> None:
        """Initialize an empty proxy store."""
        self._proxies: list[str] = []

    def add(self, proxy: str) -> None:
        """
        Add a proxy to the store.

        Args:
            proxy (str): Proxy string (e.g., "http://1.2.3.4:8080").
        """
        self._proxies.append(proxy)

    def get_all(self) -> list[str]:
        """
        Return a list of all proxies.

        Returns:
            list[str]: A copy of the stored proxies.
        """
        return list(self._proxies)

    def get_random_proxy(self) -> str | None:
        """
        Return a random proxy from the store.

        Returns:
            str | None: A randomly selected proxy if available,
            otherwise None.

        Logs:
            Debug: If the store is empty.
        """
        import random
        current_list: list[str] = self._proxies.copy()
        if not current_list:
            logger.debug("Proxy is None")
            return None
        return random.choice(current_list)

store: "ProxyStore" = ProxyStore()
