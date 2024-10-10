from imio.fpaudit.browser.settings import IFPAuditSettings
from imio.fpaudit.testing import IMIO_FPAUDIT_INTEGRATION_TESTING
from z3c.form import validator
from zope.interface import Invalid

import unittest


class TestSettings(unittest.TestCase):

    layer = IMIO_FPAUDIT_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]

    def test_validate_settings(self):
        """Check invariant"""
        invariants = validator.InvariantsValidator(None, None, None, IFPAuditSettings, None)
        # test id uniqueness
        data = {
            "log_entries": [
                {"log_id": u"a", "audit_log": u"a.log", "log_format": u"%(asctime)s - %(message)s"},
                {"log_id": u"b", "audit_log": u"b.log", "log_format": u"%(asctime)s - %(message)s"},
            ]
        }
        self.assertFalse(invariants.validate(data))
        data = {
            "log_entries": [
                {"log_id": u"a", "audit_log": u"a.log", "log_format": u"%(asctime)s - %(message)s"},
                {"log_id": u"a", "audit_log": u"b.log", "log_format": u"%(asctime)s - %(message)s"},
            ]
        }
        errors = invariants.validate(data)
        self.assertTrue(isinstance(errors[0], Invalid))
