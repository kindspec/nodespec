# SPDX-License-Identifier: Apache-2.0 OR MIT
"""`nodespec check FILE...`: one line per refusal, `file: message [identifier]`.

Exit 0 when every file is in the profile, 1 when any is refused, and 2 when
the command is used wrongly or a file cannot be read, which is no verdict.
"""

import sys

from .checker import check

USAGE = "usage: nodespec check FILE..."


def main(argv=None):
    args = sys.argv[1:] if argv is None else list(argv)
    if len(args) < 2 or args[0] != "check":
        print(USAGE, file=sys.stderr)
        return 2
    refused, unreadable = False, False
    for path in args[1:]:
        try:
            with open(path, "rb") as fh:
                data = fh.read()
        except OSError as e:
            print(f"{path}: cannot be read: {e.strerror}", file=sys.stderr)
            unreadable = True
            continue
        for f in check(data):
            refused = True
            print(f"{path}: {f.message} [{f.identifier}]")
    if unreadable:
        return 2
    return 1 if refused else 0
