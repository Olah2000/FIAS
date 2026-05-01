"""
Sebastian Olah
Muhammad Usman
Josh Rudnick
"""
 
import os
from datetime import datetime
 











class AuditLogger:
    """
    Writes a timestamped, append-only audit log to disk.

    Log format
    Each line is:
        YYYY-MM-DD HH:MM:SS | LEVEL    | EVENT_TYPE       | detail string
    Fixed-width columns make the file grep-friendly and easy to parse into a
    DataFrame if teachers ever want to analyse the audit trail programmatically.
 
    Parameters
        log_dir: directory to write log files into (created if absent)
        log_filename: name of the log file within log_dir
    """
 
    # Valid log levels — kept narrow intentionally.
    INFO  = "INFO "     # trailing space aligns with WARN in fixed columns
    WARN  = "WARN "
    ERROR = "ERROR"
 
    def __init__(self,
                 log_dir: str      = "Audit Logs/",
                 log_filename: str = "fias_audit.log") -> None:
        self.log_dir  = log_dir
        self.log_path = os.path.join(log_dir, log_filename)
        os.makedirs(log_dir, exist_ok=True)
        # Write a session-start marker so log files are easy to slice by run.
        self._write(self.INFO, "SESSION", "Application started")
 
    # ── public logging methods ────────────────────────────────────────────────
 
    def log_login(self, email: str, success: bool) -> None:
        """
        Method for recording a login attempt
 
        Parameters
        ----------
        email   : the email address that was submitted
        success : True if authentication succeeded, False otherwise
        """
        outcome = "SUCCESS" if success else "FAILURE"
        self._write(
            self.INFO if success else self.WARN,
            "LOGIN",
            f"email={email!r} outcome={outcome}"
        )
 
    def log_face_detected(self, name: str, confidence: float,
                          status: str) -> None:
        """
        Records each unique face detection that results in an attendance mark.
        Called once per student per session (not every frame) because
        AttendanceSession.mark_present() deduplicates across frames.
 
        Parameters
        ----------
        name       : student full name
        confidence : recognition confidence score (0.0–1.0)
        status     : "Present" or "Late"
        """
        self._write(
            self.INFO,
            "FACE_DETECTED",
            f"name={name!r} confidence={confidence:.2f} status={status}"
        )
 
    def log_manual_override(self, teacher_name: str, student_name: str,
                            status: str) -> None:
        """
        Records a teacher's manual attendance override (FR6 / FR20).
 
        Parameters
        ----------
        teacher_name : display name of the teacher performing the action
        student_name : full name of the student whose record was changed
        status       : new status that was applied
        """
        self._write(
            self.INFO,
            "MANUAL_OVERRIDE",
            f"teacher={teacher_name!r} student={student_name!r} "
            f"new_status={status!r}"
        )
 
    def log_student_enrolled(self, enrolling_user: str,
                              student_name: str) -> None:
        """
        Records a new face enrollment (FR2 / FR20).
 
        Parameters
        ----------
        enrolling_user : email or name of the user who performed the enrollment
        student_name   : full name of the enrolled student
        """
        self._write(
            self.INFO,
            "ENROLLMENT",
            f"enrolled_by={enrolling_user!r} student={student_name!r}"
        )
 
    def log_export(self, exported_by: str, filepath: str,
                   record_count: int) -> None:
        """
        Records a CSV export action (FR19 / FR20).
 
        Parameters
        ----------
        exported_by  : email or name of the user who triggered the export
        filepath     : path of the exported file
        record_count : number of attendance records written
        """
        self._write(
            self.INFO,
            "EXPORT",
            f"user={exported_by!r} file={filepath!r} records={record_count}"
        )
 
    def log_app_close(self) -> None:
        """Records a clean application shutdown."""
        self._write(self.INFO, "SESSION", "Application closed cleanly")
 
    def log_error(self, context: str, error: Exception) -> None:
        """
        Records an unexpected error anywhere in the application.
 
        Parameters
        ----------
        context : short description of where the error occurred
        error   : the caught exception
        """
        self._write(
            self.ERROR,
            "ERROR",
            f"context={context!r} error={type(error).__name__}: {error}"
        )
 
    # ── internal ──────────────────────────────────────────────────────────────
 
    def _write(self, level: str, event_type: str, detail: str) -> None:
        """
        Formats and appends one line to the audit log file.
 
        Format:
            2025-09-01 09:03:47 | INFO  | FACE_DETECTED    | name='John Smith' ...
 
        The file is opened and closed on every write rather than held open.
        This is intentionally conservative: it costs a small amount of I/O
        overhead but guarantees that each record is flushed to disk immediately,
        so a crash cannot cause log lines to be lost from an unflushed buffer.
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Pad event_type to 16 characters for aligned columns.
        line = f"{timestamp} | {level} | {event_type:<16} | {detail}\n"
        try:
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write(line)
        except OSError as e:
            # If we can't write the audit log, print to stderr but don't
            # crash the application — a logging failure should never take
            # down the primary attendance workflow.
            import sys
            print(f"[AuditLogger] Failed to write log: {e}", file=sys.stderr)