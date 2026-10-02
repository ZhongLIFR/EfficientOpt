from __future__ import annotations

import json

from common_model import solve_model


def solve() -> dict:
    return solve_model("technique")


if __name__ == "__main__":
    print(json.dumps(solve(), indent=2))
