# -*- coding: utf-8 -*-

from imio.fpaudit.interfaces import IImioFPAuditLayer
from imio.fpaudit.testing import IMIO_FPAUDIT_FUNCTIONAL_TESTING
from imio.helpers import HAS_PLONE_6_AND_MORE
from plone.browserlayer import utils

import unittest


if HAS_PLONE_6_AND_MORE:
    from Products.CMFPlone.utils import get_installer


class TestSetup(unittest.TestCase):

    layer = IMIO_FPAUDIT_FUNCTIONAL_TESTING

    def setUp(self):
        portal = self.layer["portal"]
        if HAS_PLONE_6_AND_MORE:
            self.installer = get_installer(portal)

    def test_product_installed(self):
        """Test if imio.fpaudit is installed with portal_quickinstaller."""
        if HAS_PLONE_6_AND_MORE:
            self.assertTrue(self.installer.is_product_installed("imio.fpaudit"))

    def test_uninstall(self):
        """Test if imio.fpaudit is cleanly uninstalled."""
        if HAS_PLONE_6_AND_MORE:
            self.installer.uninstall_product("imio.fpaudit")
            self.assertFalse(self.installer.is_product_installed("imio.fpaudit"))

    def test_browserlayer(self):
        """Test that IImioFPAuditLayer is registered."""
        if HAS_PLONE_6_AND_MORE:
            self.assertIn(IImioFPAuditLayer, utils.registered_layers())
            self.installer.uninstall_product("imio.fpaudit")
            self.assertNotIn(IImioFPAuditLayer, utils.registered_layers())
