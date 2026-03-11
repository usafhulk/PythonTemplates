"""Error Handling Configuration."""
from dataclasses import dataclass


@dataclass
class ErrorHandlingSettings:
    log_errors: bool = True
    include_traceback: bool = True
    alert_on_system_errors: bool = True
