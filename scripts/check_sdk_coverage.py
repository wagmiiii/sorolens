#!/usr/bin/env python3
"""SDK / OpenAPI coverage gate (issue #556).

Every ``operationId`` declared in ``docs/openapi.yaml`` must be reachable from
each checked SDK surface, either implemented in the SDK or documented as an
intentional exclusion in ``scripts/sdk-coverage-allowlist.json``. Every
allowlist entry carries a human-written reason; adding one is a deliberate
act, never automatic.

Checked surfaces
----------------
* ``rust``            – ``packages/rust-sdk/src/**/*.rs``. An operation is
                        exposed when a ``fn <snake_case(operationId)>`` exists
                        (the convention the ``endpoints!`` macro enforces, e.g.
                        ``getContractReport`` -> ``get_contract_report``).
* ``python_generated``– ``packages/python-sdk/src/sorolens/_generated/api``.
                        Exposed when a ``<snake_case>.py`` module generated
                        from the spec exists.
* ``python_facade``   – ``packages/python-sdk/src/sorolens/client.py``.
                        Exposed when the facade imports/calls the generated
                        ``<snake_case>`` function (the pattern every facade
                        namespace uses).

The Go client is *not* checked here: CI already regenerates it from
``docs/openapi.yaml`` in the ``go-client-stale`` job and fails on drift, which
is a stronger guarantee than name matching.

Exit status is non-zero when any operation is neither exposed nor allowlisted,
or when the allowlist contains stale entries (operation now exposed or unknown
operationId).
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.exit("pyyaml is required: pip install pyyaml")

REPO = Path(__file__).resolve().parent.parent
SPEC = REPO / "docs" / "openapi.yaml"
ALLOWLIST = REPO / "scripts" / "sdk-coverage-allowlist.json"

SNAKE_RE = re.compile(r"^[a-z][a-z0-9_]*$")


def snake_case(op_id: str) -> str:
    """camelCase / PascalCase -> snake_case (matches the SDK naming convention)."""
    s1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", op_id)
    s2 = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s1)
    return s2.lower()


def candidate_names(op_id: str) -> set[str]:
    """All plausible snake spellings for one operationId.

    ``snake_case`` alone covers the v1 conventions used by both SDKs; the
    Python generator additionally splits a leading version prefix
    (``v2GlobalStats`` -> ``v_2_global_stats``).
    """
    name = snake_case(op_id)
    out = {name}
    m = re.match(r"^v(\d+)_(.*)$", name)
    if m:
        out.add(f"v_{m.group(1)}_{m.group(2)}")
    return out


def operation_ids(spec_path: Path) -> list[str]:
    doc = yaml.safe_load(spec_path.read_text(encoding="utf-8"))
    ops: list[str] = []
    seen: set[str] = set()

    def walk(node: object) -> None:
        if isinstance(node, dict):
            op = node.get("operationId")
            if isinstance(op, str):
                if op in seen:
                    raise SystemExit(f"duplicate operationId in spec: {op}")
                seen.add(op)
                ops.append(op)
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)

    walk(doc.get("paths", {}))
    walk(doc.get("components", {}).get("callbacks", {}))
    return ops


def rust_exposed(src: Path) -> set[str]:
    found: set[str] = set()
    pattern = re.compile(r"\bfn\s+([a-zA-Z0-9_]+)\s*[(<]")
    for file in src.rglob("*.rs"):
        for match in pattern.finditer(file.read_text(encoding="utf-8")):
            name = match.group(1)
            if SNAKE_RE.match(name):
                found.add(name)
    return found


def python_generated_exposed(api_pkg: Path) -> set[str]:
    return {
        f.stem
        for f in api_pkg.rglob("*.py")
        if f.name != "__init__.py" and SNAKE_RE.match(f.stem)
    }


def python_facade_exposed(client_py: Path) -> set[str]:
    text = client_py.read_text(encoding="utf-8")
    return {
        name
        for name in re.findall(r"\b([a-z][a-z0-9_]*)\b", text)
    }


def load_allowlist(path: Path) -> dict:
    if not path.exists():
        raise SystemExit(f"missing allowlist file: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("version") != 1 or not isinstance(data.get("exemptions"), list):
        raise SystemExit(f"malformed allowlist: {path}")
    for entry in data["exemptions"]:
        if not str(entry.get("reason", "")).strip():
            raise SystemExit(
                f"allowlist entry without a reason ({entry.get('sdk')}): {entry}"
            )
    return data


def is_exempt(sdk: str, op: str, exemptions: list[dict]) -> bool:
    """True when an exact exemption or a documented glob covers (sdk, op)."""
    for e in exemptions:
        if e["sdk"] != sdk:
            continue
        pattern = e["operation"]
        if "*" in pattern or "?" in pattern:
            if fnmatch.fnmatch(op, pattern):
                return True
        elif pattern == op:
            return True
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", default=str(SPEC))
    parser.add_argument("--allowlist", default=str(ALLOWLIST))
    parser.add_argument(
        "--format", choices=("text", "json"), default="text"
    )
    args = parser.parse_args()

    ops = operation_ids(Path(args.spec))
    allow = load_allowlist(Path(args.allowlist))

    surfaces = {
        "rust": (rust_exposed(REPO / "packages" / "rust-sdk" / "src"), None),
        "python_generated": (
            python_generated_exposed(
                REPO / "packages" / "python-sdk" / "src" / "sorolens" / "_generated" / "api"
            ),
            None,
        ),
        "python_facade": (
            python_facade_exposed(
                REPO / "packages" / "python-sdk" / "src" / "sorolens" / "client.py"
            ),
            None,
        ),
    }

    exemptions = allow["exemptions"]

    gaps: list[dict] = []
    stale: list[dict] = []
    covered = 0
    exempted = 0

    known_ops = set(ops)
    for sdk, (exposed, _) in surfaces.items():
        for op in ops:
            name = snake_case(op)
            if any(c in exposed for c in candidate_names(op)):
                covered += 1
            elif is_exempt(sdk, op, exemptions):
                exempted += 1
            else:
                gaps.append({"sdk": sdk, "operationId": op, "expected_symbol": name})
        # Stale detection: exact exemptions that are now implemented, or
        # reference unknown operationIds.
        for entry in exemptions:
            if entry["sdk"] != sdk or "*" in entry["operation"] or "?" in entry["operation"]:
                continue
            if entry["operation"] not in known_ops:
                stale.append({"sdk": sdk, "operation": entry["operation"], "why": "unknown operationId"})
            elif any(c in exposed for c in candidate_names(entry["operation"])):
                stale.append({"sdk": sdk, "operation": entry["operation"], "why": "now exposed by the SDK; delete the entry"})

    # Deduplicate stale across identical sdk rows.
    unique_stale = list({json.dumps(s, sort_keys=True): s for s in stale}.values())
    unique_stale.sort(key=lambda s: (s["sdk"], s["operation"]))

    report = {
        "operations": len(ops),
        "checks": sum(len(surfaces) * len(ops) for _ in [1]),
        "covered": covered,
        "exempted": exempted,
        "gaps": gaps,
        "stale_allowlist_entries": unique_stale,
    }

    if args.format == "json":
        print(json.dumps(report, indent=2))
    else:
        print(
            f"openapi operations: {len(ops)}; "
            f"sdk surfaces checked: {len(surfaces)} "
            f"({', '.join(surfaces)})"
        )
        print(f"implemented: {covered}, allowlisted: {exempted}, gaps: {len(gaps)}")
        for gap in gaps:
            print(f"  GAP  [{gap['sdk']}] {gap['operationId']} (expected {gap['expected_symbol']})")
        for s in unique_stale:
            print(f"  STALE ALLOWLIST [{s['sdk']}] {s['operation']}: {s['why']}")
        if gaps or unique_stale:
            print(
                "\nFix: implement the operations in the SDK, or add a documented\n"
                "reason to scripts/sdk-coverage-allowlist.json. Stale allowlist\n"
                "entries must be deleted once the SDK exposes the operation.",
                file=sys.stderr,
            )

    return 1 if (gaps or unique_stale) else 0


if __name__ == "__main__":
    sys.exit(main())
