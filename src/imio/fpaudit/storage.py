from imio.fpaudit.interfaces import ILogsStorage
from zope.interface import implementer


@implementer(ILogsStorage)
class LogsStorageUtility(object):
    """Utility to store logs instances"""

    def __init__(self):
        self.storage = {}

    def add(self, key, value):
        """Add a log entry in storage."""
        self.storage[key] = value

    def set(self, dic):
        """Set storage to dic"""
        self.storage = dic

    def get(self, key, default=None):
        """Get a key from storage"""
        return self.storage.get(key, default)

    def remove(self, key):
        """Remove key from storage"""
        if key in self.storage:
            del self.storage[key]
