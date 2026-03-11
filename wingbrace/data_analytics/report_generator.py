"""
report_generator.py
===================
Generate test and data quality reports in multiple formats (HTML, CSV,
JSON, plain text) without any external dependencies.

Usage::

    from wingbrace.data_analytics import ReportGenerator

    report = ReportGenerator(title="QA Daily Report")
    report.add_section("Summary", {"total_tests": 150, "passed": 148, "failed": 2})
    report.add_table("Failed Tests", headers=["id", "name", "error"],
                     rows=[["T001", "Login", "Timeout"], ["T042", "Checkout", "500"]])
    report.add_metric("Pass Rate", "98.67%")

    # Export
    report.to_html("daily_report.html")
    report.to_json("daily_report.json")
    report.to_csv("failed_tests.csv",
                  headers=["id", "name", "error"],
                  rows=[["T001", "Login", "Timeout"]])
    print(report.to_text())
"""

import csv
import io
import json
import os
from datetime import datetime
from typing import Any


class ReportGenerator:
    """
    Build and export structured QA / data quality reports.

    Parameters
    ----------
    title:
        Report title shown in headings.
    author:
        Optional author / system name.
    """

    def __init__(
        self,
        title: str = "Report",
        author: str = "Wingbrace QA",
    ) -> None:
        self.title = title
        self.author = author
        self.created_at = datetime.now().isoformat(timespec="seconds")
        self._sections: list[dict[str, Any]] = []

    # ------------------------------------------------------------------
    # Content builders
    # ------------------------------------------------------------------

    def add_section(
        self,
        name: str,
        data: dict[str, Any],
        description: str = "",
    ) -> "ReportGenerator":
        """
        Add a key-value section (e.g. summary statistics).

        Parameters
        ----------
        name:
            Section heading.
        data:
            ``{key: value}`` pairs to display.
        description:
            Optional explanatory text shown below the heading.
        """
        self._sections.append(
            {"type": "section", "name": name, "data": data, "description": description}
        )
        return self

    def add_table(
        self,
        name: str,
        headers: list[str],
        rows: list[list[Any]],
        description: str = "",
    ) -> "ReportGenerator":
        """
        Add a tabular section.

        Parameters
        ----------
        name:
            Table heading.
        headers:
            Column headers.
        rows:
            List of row lists (values aligned to *headers*).
        """
        self._sections.append(
            {
                "type": "table",
                "name": name,
                "headers": headers,
                "rows": rows,
                "description": description,
            }
        )
        return self

    def add_metric(
        self,
        label: str,
        value: Any,
        unit: str = "",
        status: str = "",
    ) -> "ReportGenerator":
        """
        Add a single key metric.

        Parameters
        ----------
        label:
            Metric name.
        value:
            Metric value.
        unit:
            Optional unit string (e.g. ``"%"``, ``"ms"``).
        status:
            Optional status hint: ``"ok"``, ``"warn"``, or ``"error"``.
        """
        self._sections.append(
            {
                "type": "metric",
                "label": label,
                "value": value,
                "unit": unit,
                "status": status,
            }
        )
        return self

    def add_text(self, text: str, name: str = "") -> "ReportGenerator":
        """Add a free-text paragraph."""
        self._sections.append({"type": "text", "name": name, "text": text})
        return self

    def add_from_dict_list(
        self,
        name: str,
        data: list[dict[str, Any]],
        description: str = "",
        max_rows: int = 500,
    ) -> "ReportGenerator":
        """
        Add a table from a list of dicts (common data format).

        Parameters
        ----------
        data:
            List of ``dict`` rows.
        max_rows:
            Cap the number of rows rendered to avoid excessively large reports.
        """
        if not data:
            return self
        headers = list(data[0].keys())
        rows = [[row.get(h) for h in headers] for row in data[:max_rows]]
        return self.add_table(name, headers, rows, description)

    # ------------------------------------------------------------------
    # Text output
    # ------------------------------------------------------------------

    def to_text(self) -> str:
        """Render the report as plain text."""
        lines: list[str] = [
            "=" * 70,
            f"  {self.title}",
            f"  Generated: {self.created_at}  |  Author: {self.author}",
            "=" * 70,
            "",
        ]
        for section in self._sections:
            stype = section["type"]
            if stype == "section":
                lines.append(f"--- {section['name']} ---")
                if section.get("description"):
                    lines.append(section["description"])
                for k, v in section["data"].items():
                    lines.append(f"  {k}: {v}")
                lines.append("")
            elif stype == "table":
                lines.append(f"--- {section['name']} ---")
                if section.get("description"):
                    lines.append(section["description"])
                hdrs = section["headers"]
                widths = [max(len(str(h)), *(len(str(r[i])) for r in section["rows"]), 5)
                          for i, h in enumerate(hdrs)]
                sep = "  ".join("-" * w for w in widths)
                header_row = "  ".join(str(h).ljust(widths[i]) for i, h in enumerate(hdrs))
                lines += [header_row, sep]
                for row in section["rows"]:
                    lines.append("  ".join(str(v).ljust(widths[i]) for i, v in enumerate(row)))
                lines.append("")
            elif stype == "metric":
                status_tag = f" [{section['status'].upper()}]" if section.get("status") else ""
                lines.append(
                    f"  ◆ {section['label']}: {section['value']}{section.get('unit', '')}"
                    f"{status_tag}"
                )
            elif stype == "text":
                if section.get("name"):
                    lines.append(f"--- {section['name']} ---")
                lines.append(section["text"])
                lines.append("")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # JSON output
    # ------------------------------------------------------------------

    def to_json(self, filepath: str | None = None, indent: int = 2) -> str:
        """
        Render the report as JSON.

        Parameters
        ----------
        filepath:
            If provided, write to this file path.

        Returns
        -------
        str
            JSON string representation.
        """
        payload = {
            "title": self.title,
            "author": self.author,
            "created_at": self.created_at,
            "sections": self._sections,
        }
        output = json.dumps(payload, indent=indent, default=str)
        if filepath:
            os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
            with open(filepath, "w", encoding="utf-8") as fh:
                fh.write(output)
        return output

    # ------------------------------------------------------------------
    # CSV output
    # ------------------------------------------------------------------

    def to_csv(
        self,
        filepath: str,
        headers: list[str] | None = None,
        rows: list[list[Any]] | None = None,
        section_name: str | None = None,
    ) -> None:
        """
        Write a CSV file from a table section or explicit *headers*/*rows*.

        Parameters
        ----------
        filepath:
            Destination file path.
        headers / rows:
            Explicit column headers and row data.  If omitted, the first
            table section matching *section_name* is used.
        section_name:
            Name of the table section to export when *headers*/*rows* are
            not provided.
        """
        if headers is None or rows is None:
            for s in self._sections:
                if s["type"] == "table" and (
                    section_name is None or s["name"] == section_name
                ):
                    headers = s["headers"]
                    rows = s["rows"]
                    break
        if headers is None or rows is None:
            raise ValueError("No table data found to export as CSV.")

        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        with open(filepath, "w", newline="", encoding="utf-8") as fh:
            writer = csv.writer(fh)
            writer.writerow(headers)
            writer.writerows(rows)

    # ------------------------------------------------------------------
    # HTML output
    # ------------------------------------------------------------------

    def to_html(self, filepath: str | None = None) -> str:
        """
        Render the report as a styled HTML page.

        Parameters
        ----------
        filepath:
            If provided, write to this file path.

        Returns
        -------
        str
            Full HTML string.
        """
        body_parts: list[str] = []

        for section in self._sections:
            stype = section["type"]

            if stype == "section":
                rows_html = "".join(
                    f"<tr><th>{_e(k)}</th><td>{_e(v)}</td></tr>"
                    for k, v in section["data"].items()
                )
                desc = f"<p>{_e(section['description'])}</p>" if section.get("description") else ""
                body_parts.append(
                    f"<h2>{_e(section['name'])}</h2>{desc}"
                    f"<table><tbody>{rows_html}</tbody></table>"
                )

            elif stype == "table":
                headers_html = "".join(f"<th>{_e(h)}</th>" for h in section["headers"])
                rows_html = "".join(
                    "<tr>" + "".join(f"<td>{_e(v)}</td>" for v in row) + "</tr>"
                    for row in section["rows"]
                )
                desc = f"<p>{_e(section['description'])}</p>" if section.get("description") else ""
                body_parts.append(
                    f"<h2>{_e(section['name'])}</h2>{desc}"
                    f"<table><thead><tr>{headers_html}</tr></thead>"
                    f"<tbody>{rows_html}</tbody></table>"
                )

            elif stype == "metric":
                status_class = section.get("status", "")
                body_parts.append(
                    f'<div class="metric {status_class}">'
                    f'<span class="label">{_e(section["label"])}</span>'
                    f'<span class="value">{_e(section["value"])}'
                    f'{_e(section.get("unit", ""))}</span>'
                    f"</div>"
                )

            elif stype == "text":
                name_html = f"<h2>{_e(section['name'])}</h2>" if section.get("name") else ""
                body_parts.append(f"{name_html}<p>{_e(section['text'])}</p>")

        html = _HTML_TEMPLATE.format(
            title=_e(self.title),
            author=_e(self.author),
            created_at=_e(self.created_at),
            body="\n".join(body_parts),
        )

        if filepath:
            os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
            with open(filepath, "w", encoding="utf-8") as fh:
                fh.write(html)
        return html


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _e(value: Any) -> str:
    """HTML-escape a value."""
    import html
    return html.escape(str(value) if value is not None else "")


_HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 2em; color: #222; }}
    h1   {{ color: #1a3c6e; }}
    h2   {{ color: #2c5f9e; border-bottom: 1px solid #ccc; padding-bottom: 4px; }}
    table {{ border-collapse: collapse; width: 100%; margin-bottom: 1.5em; }}
    th, td {{ border: 1px solid #bbb; padding: 6px 10px; text-align: left; }}
    thead tr {{ background: #dbe8f5; }}
    tr:nth-child(even) {{ background: #f5f9ff; }}
    .metric {{ display: inline-block; margin: 6px 12px 6px 0; padding: 8px 16px;
               background: #eaf2fb; border-radius: 6px; }}
    .metric .label {{ font-weight: bold; margin-right: 8px; }}
    .metric.ok    {{ background: #d4edda; }}
    .metric.warn  {{ background: #fff3cd; }}
    .metric.error {{ background: #f8d7da; }}
    .footer {{ margin-top: 2em; font-size: 0.85em; color: #888; }}
  </style>
</head>
<body>
  <h1>{title}</h1>
  <p>Generated: <strong>{created_at}</strong> &nbsp;|&nbsp; Author: <strong>{author}</strong></p>
  {body}
  <div class="footer">Wingbrace QA Engineering &mdash; Auto-generated report</div>
</body>
</html>
"""
