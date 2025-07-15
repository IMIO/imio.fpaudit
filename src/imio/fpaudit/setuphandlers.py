# -*- coding: utf-8 -*-

from imio.fpaudit import LOG_ENTRIES_REGISTRY
from imio.fpaudit.utils import logger
from plone.registry.interfaces import IRegistry
from Products.CMFPlone.interfaces import INonInstallable
from ZODB.POSException import ConnectionStateError
from zope.component import getUtility
from zope.interface import implementer


@implementer(INonInstallable)
class HiddenProfiles(object):
    def getNonInstallableProfiles(self):
        """Hide uninstall profile from site-creation and quickinstaller."""
        return [
            "imio.fpaudit:uninstall",
        ]

    def getNonInstallableProducts(self):
        """Hide the upgrades package from site-creation and quickinstaller."""
        return ["imio.fpaudit.upgrades"]


def post_install(context):
    """Post install script"""
    registry = getUtility(IRegistry)
    if registry[LOG_ENTRIES_REGISTRY] is None:
        # may fail in tests because a datagridfield is stored, just pass in this case
        try:
            registry[LOG_ENTRIES_REGISTRY] = []
        except ConnectionStateError:
            logger.warn("!!!Failed to set registry log_entries to []!!!")
            registry.records[LOG_ENTRIES_REGISTRY].field.value_type = None


def uninstall(context):
    """Uninstall script"""
    # Do something at the end of the uninstallation of this package.
