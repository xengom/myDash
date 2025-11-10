"""System monitoring service."""

import os
import platform
from datetime import datetime
from typing import Optional
import psutil


class SystemService:
    """Provides system information and monitoring."""

    def __init__(self):
        """Initialize system service."""
        self._username = None
        self._hostname = None

    def get_username(self) -> str:
        """Get current username.

        Returns:
            Username
        """
        if not self._username:
            self._username = os.getenv('USER') or os.getenv('USERNAME') or 'unknown'
        return self._username

    def get_hostname(self) -> str:
        """Get system hostname.

        Returns:
            Hostname
        """
        if not self._hostname:
            self._hostname = platform.node()
        return self._hostname

    def get_whoami(self) -> str:
        """Get user@hostname string.

        Returns:
            user@hostname
        """
        return f"{self.get_username()}@{self.get_hostname()}"

    def get_cpu_percent(self) -> float:
        """Get current CPU usage percentage.

        Returns:
            CPU usage percentage (0-100)
        """
        return psutil.cpu_percent(interval=0.1)

    def get_memory_info(self) -> dict[str, float]:
        """Get memory usage information.

        Returns:
            Dictionary with used_gb, total_gb, and percent
        """
        mem = psutil.virtual_memory()
        return {
            'used_gb': mem.used / (1024 ** 3),
            'total_gb': mem.total / (1024 ** 3),
            'percent': mem.percent
        }

    def get_memory_percent(self) -> float:
        """Get memory usage percentage.

        Returns:
            Memory usage percentage (0-100)
        """
        return psutil.virtual_memory().percent

    def get_current_time(self) -> datetime:
        """Get current local time.

        Returns:
            Current datetime
        """
        return datetime.now()

    def format_time(self, dt: Optional[datetime] = None, format: str = "%Y-%m-%d %H:%M:%S") -> str:
        """Format datetime to string.

        Args:
            dt: Datetime to format (default: now)
            format: Format string

        Returns:
            Formatted time string
        """
        if dt is None:
            dt = self.get_current_time()
        return dt.strftime(format)

    def get_system_info(self) -> dict:
        """Get comprehensive system information.

        Returns:
            Dictionary with all system info
        """
        mem_info = self.get_memory_info()

        return {
            'whoami': self.get_whoami(),
            'username': self.get_username(),
            'hostname': self.get_hostname(),
            'cpu_percent': self.get_cpu_percent(),
            'memory_used_gb': mem_info['used_gb'],
            'memory_total_gb': mem_info['total_gb'],
            'memory_percent': mem_info['percent'],
            'current_time': self.get_current_time(),
            'platform': platform.system(),
            'platform_release': platform.release(),
            'python_version': platform.python_version(),
        }

    def format_status_line(self) -> str:
        """Format system status for header display.

        Returns:
            Formatted status string
        """
        cpu = self.get_cpu_percent()
        mem = self.get_memory_percent()
        time_str = self.format_time(format="%H:%M:%S")
        whoami = self.get_whoami()

        return f"👤 {whoami} | 🖥️  CPU: {cpu:.1f}% | 💾 MEM: {mem:.1f}% | 🕐 {time_str}"
