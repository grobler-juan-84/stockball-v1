"""Reset / rebuild the research database.

DESTRUCTIVE: this command will eventually drop and repopulate the database.
It is intentionally unimplemented until reset behavior is deliberately designed.
"""

from __future__ import annotations

import sys


def main() -> None:
    print(
        "reset_database is intentionally unimplemented.\n"
        "Destructive reset behavior will be designed before this command is enabled.",
        file=sys.stderr,
    )
    raise SystemExit(1)


if __name__ == "__main__":
    main()
