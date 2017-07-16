# import os

# OSINFO = {'id':'plantform', 'pretty_name':'version'}
# SUPPORTEDOS = ['opensuse']
# class ChangeRepo(object):
# 	"""change repository to chinese mirror"""
# 	def __init__(self, plantform=''):
# 		if not plantform:
# 			versions = os.popen('cat /etc/os-release').readlines()
# 			for line in versions:
# 				tmp = line.strip().replace('"','').split('=')
# 				if tmp[0].lower() in OSINFO:
# 					setattr(self, plantform, tmp[1])

import os
import sys
import changeRepo as cr
import unittest
from unittest import mock


_supported = ['supported system', 'change repositories',
              'install pop software', 'install basic software', 'adding imporved bashrc', 'install pip module']


class BaseChangeRepoTest(unittest.TestCase):
    """basic tests set for changeRepo.py"""

    class ChangeRepo(cr.ChangeRepo):
        def _chk_permission(self):
            pass

    # def setUp(self):
    #     pass


class TestChangeRepo(BaseChangeRepoTest):
    def test_supported_system(self):
        self.assertIn('opensuse', cr.SUPPORTEDOS)

    def test_change_repo(self):
        reposurl = []
        plantform = 'tumbleweed'
        # mirror = 'https://mirrors.tuna.tsinghua.edu.cn/'+plantform
        mirror = 'https://mirrors.ustc.edu.cn/' + plantform
        with mock.patch('os.system', lambda x: reposurl.append(x)):
            cr.changerepo(plantform=plantform, mirrorname='ustc')
        self.assertTrue(reposurl)
        self.assertTrue(
            all([mirror in url for url in reposurl if url.startswith('sudo zypper addrepo')]))

    # @unittest.skip
    def test_install_software(self):
        infos = []
        softs = ['imagewriter']
        with mock.patch('os.system', lambda x: infos.append(x)):
            cr.install_software(plantform='opensuse', softs=softs)
        softs1 = [ '-t pattern devel_basis', 'chromium', 'git', 'fcitx-table-cn-wubi-pinyin', 'ctags',]
        softs.extend(softs1)
        with mock.patch('os.system', lambda x: infos.append(x)):
            cr.install_software(plantform='opensuse')
        patts = ['sudo zypper in -y %s' % soft for soft in softs]
        self.assertTrue(infos)
        self.assertEqual(infos, patts)

    # @unittest.skip
    def test_install_pip_module(self):
        patts = ['sudo pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/',
                 'sudo pip install -i https://pypi.tuna.tsinghua.edu.cn/simple/ selenium',
                 'sudo pip install -r requirement.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/',
                 'sudo pip install -i https://pypi.tuna.tsinghua.edu.cn/simple/ virtualenvwrapper'
                 ]
        infos = []
        with mock.patch('os.system', lambda x: infos.append(x)):
            cr.install_pip_module(file='requirements.txt', softs=['selenium'])

        with mock.patch('os.system', lambda x: infos.append(x)):
            cr.install_pip_module(file='requirement.txt')
        
        self.assertTrue(infos)
        self.assertEqual(infos, patts)

    # @unittest.skip
    def test_improved_bash(self):
        infos = []
        patts = ['echo "alias grep=\'grep -E --color=auto\'" >> /home/dev/.bashrc',
                 'echo PATH=~/.local/bin:$PATH >> /home/dev/.bashrc',
                 'echo export PATH=~/bin:$PATH >> /home/dev/.bashrc']
        with mock.patch('os.system', lambda x: infos.append(x)):
            cr.improved_bash()

        self.assertTrue(infos)
        self.assertEqual(infos, patts)

    @unittest.skip
    def test_update_hosts(self):
        infos = []
        with mock.patch('os.system', lambda x: infos.append(x)):
            cr.get_hosts()
        self.assertTrue(os.path.exists('hosts'))
        self.assertTrue(os.path.exists('hosts_test'))
        hosts = open('hosts').read()
        hosts_test = open('hosts_test').read()
        self.assertTrue(infos)
        self.assertEqual(hosts, hosts_test)

    def test_get_user_info(self):
        infos = cr.get_userinfo(1100)
        self.assertEqual(infos,(None,None))
        infos = cr.get_userinfo()
        self.assertEqual(infos, ('dev', '/home/dev'))

    def test_add_repos(self):
        infos = []
        patts = [
            'sudo zypper ar -fc https://mirrors.tuna.tsinghua.edu.cn/packman/suse/openSUSE_Leap_42.2/ tuna-packman',
            'sudo zypper ar -fc http://download.opensuse.org/repositories/devel:/languages:/python3/openSUSE_Leap_42.2/ dev-py3',
            'sudo rpm -v --import https://download.sublimetext.com/sublimehq-rpm-pub.gpg',
            'sudo rpm --import https://packages.microsoft.com/keys/microsoft.asc',
            'sudo zypper addrepo -g -f https://download.sublimetext.com/rpm/stable/x86_64/sublime-text.repo',
            'sudo sh -c \'echo -e "[code]\\nname=Visual Studio Code\\nbaseurl=https://packages.microsoft.com/yumrepos/vscode\\nenabled=1\\ntype=rpm-md\\ngpgcheck=1\\ngpgkey=https://packages.microsoft.com/keys/microsoft.asc" > /etc/zypp/repos.d/vscode.repo\''
        ]
        with mock.patch('os.system', lambda x: infos.append(x)):
            notnone = cr.add_repos()
        self.assertTrue(notnone)
        self.assertEqual(infos, patts)

    def test_plantform(self):
        instance = self.ChangeRepo()
        self.assertEqual(instance.plantform, 'opensuse')
        self.assertEqual(instance.version, '42.2')

    def test_add_group(self):
        infos = []
        patts = [
            'sudo usermod -aG vboxusers dev',
            'sudo usermod -aG docker dev'
        ]
        with mock.patch('os.system', lambda x: infos.append(x)):
            cr.add_group()
        
        self.assertTrue(infos)
        self.assertEqual(infos, patts)
        

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
