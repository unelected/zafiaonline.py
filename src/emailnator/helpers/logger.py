# Copyright (C) 2025 unelected
#
# This file is part of email_generator.
#
# account_generator is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# account_generator is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with account_generator. If not, see
# <https://www.gnu.org/licenses/>.

"""
Configures and initializes the "email_generator" logger.

The logger outputs logs to both the console and a rotating file.

Console handler:
    Level: INFO
    Format: "%(asctime)s | %(levelname)s | %(message)s"

Rotating file handler:
    Level: DEBUG
    File: "email_generator.log"
    Format: "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    Rotation: max 500 KB per file, up to 3 backup files.

Typical Usage Example:
    from this_module import logger
    logger.info("Email generation started")
    logger.debug("Debug details about processing")
    logger.error("Something went wrong")

Attributes:
    logger (logging.Logger): Configured logger instance.
"""
import logging

from logging.handlers import RotatingFileHandler


logger: logging.Logger = logging.getLogger("email_generator")
logger.setLevel(logging.DEBUG)

logger.handlers.clear()

console_handler: logging.StreamHandler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_formatter: logging.Formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(message)s"
)
console_handler.setFormatter(console_formatter)
logger.addHandler(console_handler)

file_handler: RotatingFileHandler = RotatingFileHandler(
    "email_generator.log",
    maxBytes=500_000,
    backupCount=3,
    encoding="utf-8"
)
file_handler.setLevel(logging.DEBUG)
file_formatter: logging.Formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)

