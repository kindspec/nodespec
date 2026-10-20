# SPDX-License-Identifier: Apache-2.0 OR MIT
"""The checker's identifiers are SPEC.md §9's, read from SPEC.md itself."""

import os
import re

from nodespec import ID_ENTRIES, IDENTIFIERS
from nodespec.checker import MAX_EDGES

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def section_9():
    with open(os.path.join(ROOT, "SPEC.md"), encoding="utf-8") as fh:
        text = fh.read()
    start = text.index("## 9. Refusals")
    return text[start : text.index("## 10.", start)]


def test_identifiers_are_section_9s_list_in_order():
    listed = re.findall(r"^\s*\d+\.\s+`([a-z-]+)`:", section_9(), re.M)
    assert len(listed) == 29
    assert tuple(listed) == IDENTIFIERS


def test_id_entries_are_section_9s():
    s9 = section_9()
    block = s9[s9.index("Some entries are about an id") : s9.index("The other entries")]
    named = set()
    for item in " ".join(block.split()).split(" - ")[1:]:
        named |= set(re.findall(r"`([a-z-]+)`", item.split(":")[0]))
    assert named == ID_ENTRIES


def test_edge_limit_is_section_4_6s():
    with open(os.path.join(ROOT, "SPEC.md"), encoding="utf-8") as fh:
        assert f"more than {MAX_EDGES} edges is refused" in " ".join(fh.read().split())
