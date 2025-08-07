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

import zafiaonline.utils as utils
import zafiaonline.structures as structures
import zafiaonline.api_client as api_client
import zafiaonline.transport as transport

from zafiaonline.main import Client

__all__: tuple[str, ...] = (
    # Classes
    "Client",

    # Directories
    "transport",
    "utils",
    "structures",
    "api_client",
)
