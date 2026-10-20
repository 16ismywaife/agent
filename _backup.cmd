@echo off
REM Backup HANDBOOK.md + notes/log.md to E:\05_docs (see _backup.ps1 for detail).
REM
REM Why this .cmd wrapper exists:
REM   This machine's PowerShell execution policy is Restricted, so running
REM   .\_backup.ps1 directly fails with "running scripts is disabled on this system".
REM   The wrapper applies -ExecutionPolicy Bypass for THIS call only; it does not
REM   change any system setting.
REM
REM NOTE: keep this file ASCII-only. cmd.exe reads .cmd with the OEM codepage,
REM       so non-ASCII comments get mangled and can break parsing.
REM
REM Usage: double-click this file, or run _backup.cmd in a terminal.

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0_backup.ps1" %*
set RC=%ERRORLEVEL%

echo.
pause
exit /b %RC%
