from imio.fpaudit import LOG_DIR
from imio.fpaudit import LOG_ENTRIES_REGISTRY
from imio.fpaudit.interfaces import ILogsStorage
from imio.fpaudit.logger import FPAuditLogInfo
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
from zope.component import queryUtility
from zope.interface import implementer

import os


def _build_storage(logs_config):
    """Build a dict of FPAuditLogInfo instances from a logs config list."""
    dic = {}
    for entry in logs_config:
        log_i = FPAuditLogInfo(
            {"audit-log": os.path.join(LOG_DIR, entry["audit_log"])},
            entry["log_id"],
            logformat=entry["log_format"],
        )
        log_i.handler.formatter.datefmt = "%Y-%m-%d %H:%M:%S"
        dic[entry["log_id"]] = log_i
    return dic


@implementer(ILogsStorage)
class LogsStorageUtility(object):
    """Utility to store logs instances"""

    def __init__(self):
        self.storage = {}
        self._loaded = False

    def _ensure_loaded(self):
        """Lazily populate storage from registry on first access."""
        if self._loaded:
            return
        registry = queryUtility(IRegistry)
        if registry is not None:
            log_entries = registry.get(LOG_ENTRIES_REGISTRY) or []
            if log_entries:
                self.storage = _build_storage(log_entries)
        self._loaded = True

    def add(self, key, value):
        """Add a log entry in storage"""
        self.storage[key] = value

    def set(self, dic):
        """Set storage to dic"""
        self.storage = dic
        self._loaded = True

    def get(self, key, default=None):
        """Get a key from storage"""
        self._ensure_loaded()
        return self.storage.get(key, default)

    def remove(self, key):
        """Remove key from storage"""
        if key in self.storage:
            del self.storage[key]


def store_config(logs_config):
    """Store logs configuration in utility."""
    storage = getUtility(ILogsStorage)
    storage.set(_build_storage(logs_config))
