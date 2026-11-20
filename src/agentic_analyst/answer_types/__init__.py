"""One module per answer type, discovered automatically (see `routing.py`).

To add an answer type, add a module here that defines:
    PATTERN: regex (matched case-insensitively against the Question)
    PRIORITY: int, lower is tried first (default 100)
    def answer(series, i, question) -> Draft | None     # i is the period index the Question is about
and register any new measures its Claims need with `measures.register_measure`.
No shared file needs editing.
"""
