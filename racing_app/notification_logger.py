"""
Notification Logger - Displays events in both terminal and overlay

@nandurstudio
Date Created: 2025-12-20
Last Modified: 2026-02-03
"""

import logging
from datetime import datetime
from typing import Optional, Callable


class NotificationLogger:
    """
    Centralized logging system that outputs to both terminal and overlay
    Similar to Rust's notification system
    """
    
    def __init__(self, overlay_callback: Optional[Callable] = None):
        """
        Initialize notification logger
        
        Args:
            overlay_callback: Optional callback to send notifications to overlay
                             Called as: callback(message, type)
                             Types: 'success', 'warning', 'error', 'info'
        """
        self.logger = logging.getLogger(__name__)
        self.overlay_callback = overlay_callback
        
    def notify(self, message: str, type_: str = "info"):
        """
        Send notification to both terminal and overlay
        
        Args:
            message: Notification message
            type_: Type of notification ('info', 'success', 'warning', 'error')
        """
        # Log to terminal
        if type_ == "error":
            self.logger.error(message)
        elif type_ == "warning":
            self.logger.warning(message)
        elif type_ == "success":
            self.logger.info(f"✓ {message}")
        else:  # info
            self.logger.info(message)
        
        # Send to overlay if callback available
        if self.overlay_callback:
            try:
                self.overlay_callback(message, type_)
            except Exception as e:
                self.logger.debug(f"Failed to send notification to overlay: {e}")
    
    def command_received(self, username: str, command: str, key: Optional[str]):
        """Log when command received"""
        if key:
            msg = f"[{username}] {command} → {key}"
            self.notify(msg, "info")
        else:
            msg = f"[{username}] {command} (unknown)"
            self.notify(msg, "warning")
    
    def success(self, message: str):
        """Log success event"""
        self.notify(message, "success")
    
    def warning(self, message: str):
        """Log warning event"""
        self.notify(message, "warning")
    
    def error(self, message: str):
        """Log error event"""
        self.notify(message, "error")
    
    def info(self, message: str):
        """Log info event"""
        self.notify(message, "info")


class OverlayNotificationManager:
    """
    Manages notifications for overlay via file-based or socket communication
    """
    
    def __init__(self, notification_file: str = "notifications.log"):
        """
        Initialize overlay notification manager
        
        Args:
            notification_file: File to write notifications (for polling)
        """
        self.notification_file = notification_file
        self.logger = logging.getLogger(__name__)
    
    def send(self, message: str, type_: str = "info"):
        """
        Send notification to overlay via file
        
        Args:
            message: Message to send
            type_: Type of notification
        """
        try:
            # Write to notification file with timestamp
            with open(self.notification_file, 'a', encoding='utf-8') as f:
                timestamp = datetime.now().isoformat()
                f.write(f"{timestamp}|{type_}|{message}\n")
        except Exception as e:
            self.logger.debug(f"Failed to write notification: {e}")
    
    def send_special_command(self, command: str, data: str = ""):
        """
        Send special command to overlay (username update, etc)
        
        Args:
            command: Command type ('update-username', etc)
            data: Data payload for the command
        """
        try:
            with open(self.notification_file, 'a', encoding='utf-8') as f:
                timestamp = datetime.now().isoformat()
                f.write(f"{timestamp}|COMMAND|{command}:{data}\n")
        except Exception as e:
            self.logger.debug(f"Failed to write special command: {e}")
    
    def send_event(self, event_type: str, event_data: dict):
        """
        Send event to overlay via HTTP (for real-time IPC) - NON-BLOCKING
        
        Args:
            event_type: Type of event ('camera-event', 'drift-event', etc)
            event_data: Event data as dictionary
        """
        import json
        import httpx
        import threading
        
        def _send_async():
            """Send HTTP request in background thread to prevent blocking"""
            try:
                # Fast timeout (0.3s) to prevent hang on rapid events
                with httpx.Client(timeout=0.3) as client:
                    response = client.post(
                        'http://localhost:9999/ipc',
                        json={'event': event_type, 'data': event_data}
                    )
                    if response.status_code == 200:
                        self.logger.debug(f"IPC ✓ {event_type}")
                    else:
                        self.logger.debug(f"IPC ✗ {event_type} ({response.status_code})")
            except httpx.TimeoutException:
                self.logger.debug(f"IPC timeout: {event_type} (overlay slow/not running)")
            except Exception as http_err:
                self.logger.debug(f"IPC error ({event_type}): {http_err}")
        
        # Fire-and-forget: Send in background thread (non-blocking)
        thread = threading.Thread(target=_send_async, daemon=True)
        thread.start()