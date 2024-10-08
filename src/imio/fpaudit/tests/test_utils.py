from imio.fpaudit import LOG_DIR
from imio.fpaudit.storage import store_config
from imio.fpaudit.testing import clear_temp_dir
from imio.fpaudit.testing import IMIO_FPAUDIT_INTEGRATION_TESTING
from imio.fpaudit.testing import write_temp_files
from imio.fpaudit.utils import fplog
from imio.fpaudit.utils import get_all_lines_of
from imio.fpaudit.utils import get_lines_of
from imio.fpaudit.utils import get_logrotate_filenames
from plone import api

import os
import shutil
import tempfile
import unittest


class TestUtils(unittest.TestCase):

    layer = IMIO_FPAUDIT_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        api.portal.set_registry_record(
            "imio.fpaudit.settings.log_entries",
            [{"log_id": u"test", "audit_log": u"test_utils.log", "log_format": u"%(asctime)s - %(message)s"}],
        )

    def test_fplog(self):
        log_file_path = os.path.join(LOG_DIR, "test_utils.log")
        for fil in get_logrotate_filenames(LOG_DIR, "test_utils.log", r".+$"):
            os.remove(fil)
        fplog("test", "AUDIT", "extra 1")
        logs = get_logrotate_filenames(LOG_DIR, "test_utils.log", r"\.\d+$")
        self.assertListEqual(logs, [log_file_path])
        lines = [ln for ln in get_lines_of(log_file_path)]
        self.assertEqual(len(list(lines)), 1)
        self.assertTrue(lines[0].endswith(" - user=test_user_1_ ip=None action=AUDIT extra 1"))
        fplog("test", "AUDIT", "extra 2")
        lines = [ln for ln in get_lines_of(log_file_path)]
        self.assertEqual(len(list(lines)), 2)
        self.assertTrue(lines[0].endswith(" - user=test_user_1_ ip=None action=AUDIT extra 2"))
        self.assertTrue(lines[1].endswith(" - user=test_user_1_ ip=None action=AUDIT extra 1"))
        # check with logrotated files
        log_file_path1 = log_file_path + ".1"
        os.rename(log_file_path, log_file_path1)
        # changed id to stop writing in rotated here
        store_config([{"log_id": u"test1", "audit_log": u"test_utils.log", "log_format": u"%(asctime)s - %(message)s"}])
        fplog("test1", "AUDIT", "extra 3")
        fplog("test1", "AUDIT", "extra 4")
        logs = get_logrotate_filenames(LOG_DIR, "test_utils.log", r"\.\d+$")
        lines = [ln for ln in get_all_lines_of(logs)]
        self.assertTrue(lines[0].endswith(" - user=test_user_1_ ip=None action=AUDIT extra 4"))
        self.assertTrue(lines[1].endswith(" - user=test_user_1_ ip=None action=AUDIT extra 3"))
        self.assertTrue(lines[2].endswith(" - user=test_user_1_ ip=None action=AUDIT extra 2"))
        self.assertTrue(lines[3].endswith(" - user=test_user_1_ ip=None action=AUDIT extra 1"))
        for fil in get_logrotate_filenames(LOG_DIR, "test_utils.log", r".+$"):
            os.remove(fil)

    def test_get_logrotate_filenames(self):
        temp_dir = tempfile.mkdtemp()
        try:
            # check filter
            write_temp_files(temp_dir, ["test.log", "other.log", "test.log.1", "test.log.2", "test.log.lock"])
            expected_files = ["test.log", "test.log.1", "test.log.2"]
            result_files = get_logrotate_filenames(temp_dir, "test.log", r"\.\d+$", full=False)
            self.assertListEqual(result_files, expected_files)
            clear_temp_dir(temp_dir)
            # check order
            write_temp_files(temp_dir, ["test.log", "test.log.1", "test.log.2", "test.log.10"])
            expected_files = ["test.log", "test.log.1", "test.log.2", "test.log.10"]
            result_files = get_logrotate_filenames(temp_dir, "test.log", r"\.\d+$", full=False)
            self.assertListEqual(result_files, expected_files)
            clear_temp_dir(temp_dir)
            # check full path
            write_temp_files(temp_dir, ["test.log", "test.log.1", "test.log.2", "test.log.10"])
            expected_files = ["test.log", "test.log.1", "test.log.2", "test.log.10"]
            expected_files = [os.path.join(temp_dir, f) for f in expected_files]
            result_files = get_logrotate_filenames(temp_dir, "test.log", r"\.\d+$")
            self.assertListEqual(result_files, expected_files)
            clear_temp_dir(temp_dir)
            # checl another filter
            write_temp_files(
                temp_dir, ["test.log", "other.log", "test.log-20240825", "test.log-20240901", "test.log-20240908"]
            )
            expected_files = ["test.log", "test.log-20240825", "test.log-20240901", "test.log-20240908"]
            result_files = get_logrotate_filenames(temp_dir, "test.log", r"-\d{8}$", full=False)
            self.assertListEqual(result_files, expected_files)
        finally:
            shutil.rmtree(temp_dir)
