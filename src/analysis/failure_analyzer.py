"""Rule-based logcat triage.

Head unit test runs produce a lot of logcat noise. Rather than making a
human scroll through it after every failure, this module classifies each
line against a small set of known-bad signatures (ANR, fatal crash,
watchdog reset, service timeout) and rolls the results up into a short
summary that gets attached to the pytest report. It's a deliberately
simple, explainable rule engine - not an ML/LLM classifier - which keeps
its verdicts reproducible and easy to extend with new signatures.
"""
from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass, field

_SIGNATURES: dict[str, re.Pattern] = {
    "anr": re.compile(r"ActivityManager: ANR in (?P<component>\S+)"),
    "crash": re.compile(r"FATAL EXCEPTION.*?(?P<component>[\w.]+Exception)"),
    "watchdog_reset": re.compile(r"Watchdog: \*\*\* WATCHDOG KILLING"),
    "service_timeout": re.compile(r"ServiceTimeoutException|TimeoutException"),
    "boot_failure": re.compile(r"BOOT_COMPLETE.*fail", re.IGNORECASE),
}


@dataclass
class TriageResult:
    total_lines: int
    findings: list[dict] = field(default_factory=list)
    counts: Counter = field(default_factory=Counter)

    @property
    def is_clean(self) -> bool:
        return not self.findings

    def summary(self) -> str:
        if self.is_clean:
            return f"no known failure signatures in {self.total_lines} log lines"
        breakdown = ", ".join(f"{count}x {kind}" for kind, count in self.counts.most_common())
        return f"{len(self.findings)} issue(s) found in {self.total_lines} lines ({breakdown})"


class FailureAnalyzer:
    def analyze(self, log_lines: list[str]) -> TriageResult:
        result = TriageResult(total_lines=len(log_lines))
        for line in log_lines:
            for kind, pattern in _SIGNATURES.items():
                match = pattern.search(line)
                if match:
                    component = match.groupdict().get("component", "unknown")
                    result.findings.append({"kind": kind, "component": component, "line": line})
                    result.counts[kind] += 1
                    break
        return result
