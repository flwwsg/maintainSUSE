import os
import sys
from custom import Ubuntu, Opensuse
import unittest
from unittest import mock
import json

class MockUbuntu(Ubuntu):
    def _chk_permission(self):
        pass

    def chk_url(self, *arg, **kwargs):
        pass

class MockOpensuse(Opensuse):
    def _chk_permission(self):
        pass

    def chk_url(self, *arg, **kwargs):
        pass

class TestInitialzeUbuntu(unittest.TestCase):
    def setUp(self):
        self.configs = json.load(open('configs.json'))
        self.cr = MockUbuntu('16.04', 'tuna', 'configs.json')
        self.cr.check_prerequirements()
        self.plantform = self.cr.plantform

    def mock_system(self, infos, func):
        with mock.patch('os.system', lambda x: infos.append(x)):
            if callable(func):
                func()
            elif hasattr(self, func):
                getattr(self, func)()
            else:
                raise ValueError('Not supported function %s' % func)

    def test_get_hosts(self):
        if os.path.exists('hosts'):
            os.remove('hosts')
        with mock.patch('os.system', lambda x: print(x)):
            self.cr.get_hosts()
        self.assertTrue(os.path.exists('hosts'))
        self.assertTrue(open('hosts').read())

    @unittest.skip
    def test_add_repos(self):
        infos = []
        self.mock_system(infos, self.cr.add_repo)


    def test_install_software(self):
        pass


class TestInitialzeOpensuse(unittest.TestCase):
        def setUp(self):
            self.configs = json.load(open('configs.json'))
            self.cr = MockUbuntu('42.3', 'ustc', 'configs.json')
            self.cr.check_prerequirements()
            self.plantform = self.cr.plantform

        def mock_system(self, infos, func):
            with mock.patch('os.system', lambda x: infos.append(x)):
                if callable(func):
                    func()
                elif hasattr(self, func):
                    getattr(self, func)()
                else:
                    raise ValueError('Not supported function %s' % func)
                
        def test_change_repo_opensuse(self):
            infos = []
            self.mock_system(infos, self.cr.add_repo)
            self.assertTrue(infos)
            c_repos = self.configs[self.plantform]['custom_repos']
            self.assertTrue(all([url.startswith('sudo zypper addrepo') for url in infos if url not in c_repos]))
    
# if __name__ == '__main__':
#     print('starting test....')
    # help text
# 	print('enter you want to test:')

# 	maxlen = 0
# 	for l in _supported:
# 		if maxlen < len(l):
# 			maxlen = len(l)
# 	for i, item in enumerate(_supported):
# 		print(item,' '*(maxlen-len(item)), 'enter:', i)
# 	print('if you want to test all set ,enter "all". \
# eg: I want to test "supported system and change repositories", so I enter "1,2"'
# 		)
# 	testset = input(':')

# Failed to restart NetworkManager.service: Unit NetworkManager.service not found