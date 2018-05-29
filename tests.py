import os
from custom_os import Opensuse, VAR_MAPPING
import unittest
from unittest import mock
import json


# class MockUbuntu(Ubuntu):
#     def _chk_permission(self):
#         pass
#
#     def chk_url(self, *arg, **kwargs):
#         pass


class MockOpenSUSE(Opensuse):
    def check_requirement(self):
        return


class TestOpenSUSE(unittest.TestCase):
    def setUp(self):
        self.configs = json.load(open('configs.json'))
        self.os = MockOpenSUSE("15.0", 'tuna')

    def test_var(self):
        self.os.get_var()
        self.assertTrue(all([v != "" for k, v in VAR_MAPPING.items()]))
        self.assertEqual(VAR_MAPPING["FULL_SUSE_VERSION"], "openSUSE_Leap_15.0")
        self.assertEqual(VAR_MAPPING["MIRROR_NAME"], "tuna")

    # def test_clear_repos(self):
    #     with mock.patch('os.unlink', lambda x: print(x)):
    #         self.os.clear_repos()

    def test_add_repo(self):
        cmd = []
        with mock.patch("os.system", lambda x: cmd.append(x)):
            self.os.add_repo()

        for i in cmd:
            if not i.startswith("sudo zypper addrepo --check --refresh --name"):
                continue

    def test_install_soft(self):
        cmd = []
        with mock.patch("os.system", lambda x: cmd.append(x)):
            self.os.install_software()
        for i in cmd:
            if not i.startswith("sudo zypper in -y"):
                self.fail("fail to install software under command \"%s\"" % i)

    def test_add_bash_rc(self):
        pass


# class TestInitializeUbuntu(unittest.TestCase):
#     def setUp(self):
#         self.configs = json.load(open('configs.json'))
#         self.cr = MockUbuntu('16.04', 'tuna', 'configs.json')
#         self.cr.check_prerequirements()
#         self.plantform = self.cr.platform
#
#     def mock_system(self, infos, func):
#         with mock.patch('os.system', lambda x: infos.append(x)):
#             if callable(func):
#                 func()
#             elif hasattr(self, func):
#                 getattr(self, func)()
#             else:
#                 raise ValueError('Not supported function %s' % func)
#
#     def test_get_hosts(self):
#         if os.path.exists('hosts'):
#             os.remove('hosts')
#         with mock.patch('os.system', lambda x: print(x)):
#             self.cr.get_hosts()
#         self.assertTrue(os.path.exists('hosts'))
#         self.assertTrue(open('hosts').read())
#
#     @unittest.skip
#     def test_add_repos(self):
#         infos = []
#         self.mock_system(infos, self.cr.add_repo)
#
#
#     def test_install_software(self):
#         pass

