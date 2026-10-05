# Critical System Processes Runbook

The following processes are critical for the operating system and MUST NOT be terminated under any circumstances.

## Windows Critical Processes
- `explorer.exe`: The main Windows graphical shell. Killing this will remove the taskbar and desktop icons.
- `svchost.exe`: Host process for Windows services.
- `System`: NT Kernel & System process.
- `smss.exe`: Session Manager Subsystem.
- `csrss.exe`: Client/Server Run-Time Subsystem.
- `wininit.exe`: Windows Start-Up Application.
- `winlogon.exe`: Windows Logon Process.
- `services.exe`: Services Control Manager.
- `lsass.exe`: Local Security Authority Process.
- `taskmgr.exe`: Task Manager.

## Mac/Linux Critical Processes
- `kernel_task`: Mac kernel process.
- `launchd`: Mac initialization process.
- `systemd`: Linux initialization process.
- `init`: Linux initialization process.
- `WindowServer`: Mac window manager.

If a process name matches or resembles any of these, it must be considered CRITICAL and marked as `is_critical: true`.
