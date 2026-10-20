# SPDX-License-Identifier: Apache-2.0 OR MIT
"""nodespec's reference checker for SPEC.md draft 0."""

from .checker import ID_ENTRIES, IDENTIFIERS, Finding, check

__all__ = ["ID_ENTRIES", "IDENTIFIERS", "Finding", "check", "__version__"]
__version__ = "0.0.0"
