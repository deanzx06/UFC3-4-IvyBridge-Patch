# SPDX-License-Identifier: GPL-2.0-only
"""Pre-compiled Ivy Bridge compatibility translation plan for UFC 4 PS4 Port (CUSA14204 v28.00).
Generated with tools/build_cpu_compat.py (9,690 translated sites, 0 unhandled).
Zero binary game leaks (uses standard library LZMA + Base64, zero external dependencies).
"""
import base64
import json
import lzma

try:
    from .legacy_plan_p1 import PART1
    from .legacy_plan_p2 import PART2
    from .legacy_plan_p3 import PART3
    from .legacy_plan_p4 import PART4
except ImportError:
    from legacy_plan_p1 import PART1
    from legacy_plan_p2 import PART2
    from legacy_plan_p3 import PART3
    from legacy_plan_p4 import PART4

def get_plan():
    """Returns the decompressed compatibility plan dictionary."""
    combined = PART1 + PART2 + PART3 + PART4
    return json.loads(lzma.decompress(base64.b64decode(combined.encode("ascii"))))
