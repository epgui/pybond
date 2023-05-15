from gc import collect, get_referrers
from typing import Any

from pytest import MonkeyPatch


def _is_referrer_a_module(d: dict) -> bool:
    return isinstance(d, dict) and "__loader__" in d.keys()


def replace_bound_references_in_memory(
    monkeypatch_ctx: MonkeyPatch,
    target_obj: Any,
    new_obj: Any,
) -> None:
    collect()  # Perform GC before checking for references in memory
    for reference in get_referrers(target_obj):
        if _is_referrer_a_module(reference):
            for k, v in reference.items():
                if v is target_obj:
                    monkeypatch_ctx.setitem(reference, k, new_obj)
