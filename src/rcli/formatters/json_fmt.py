"""JSON output formatter."""

from __future__ import annotations

import json
import sys


class JsonFormatter:
    """Outputs data as JSON to stdout."""

    def output_item(self, item) -> None:
        json.dump(item.to_dict(), sys.stdout, indent=2)
        sys.stdout.write("\n")

    def output_list(self, items: list) -> None:
        data = [i.to_dict() for i in items]
        json.dump(data, sys.stdout, indent=2)
        sys.stdout.write("\n")

    def output_tree(self, requirements: list) -> None:
        data = [r.to_dict() for r in requirements]
        json.dump(data, sys.stdout, indent=2)
        sys.stdout.write("\n")

    def output_search(self, results: list[tuple[int, object]]) -> None:
        data = [{"score": score, **item.to_dict()} for score, item in results]
        json.dump(data, sys.stdout, indent=2)
        sys.stdout.write("\n")

    def output_status(self, status_data: dict) -> None:
        json.dump(status_data, sys.stdout, indent=2)
        sys.stdout.write("\n")

    def output_export(self, data: dict) -> str:
        return json.dumps(data, indent=2) + "\n"

    def output_message(self, message: str, data: object | None = None) -> None:
        out: dict = {"message": message}
        if data is not None:
            out["data"] = data.to_dict()
        json.dump(out, sys.stdout, indent=2)
        sys.stdout.write("\n")
