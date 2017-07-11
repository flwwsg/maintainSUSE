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
	pass

class TestChangeRepo(BaseChangeRepoTest):
	def test_supported_system(self):
		self.assertIn('opensuse', cr.SUPPORTEDOS)
			
	def test_change_repo(self):
		reposurl = []
		plantform = 'tumbleweed'
		# mirror = 'https://mirrors.tuna.tsinghua.edu.cn/'+plantform
		mirror = 'https://mirrors.ustc.edu.cn/'+plantform
		with mock.patch('os.system', lambda x: reposurl.append(x)):
			cr.changerepo(plantform=plantform, mirrorname='ustc')
		self.assertTrue(reposurl)
		self.assertTrue(all([mirror in url for url in reposurl if url.startswith('sudo zypper addrepo')]))

	# @unittest.skip
	def test_install_software(self):
		infos = []
		softs = ['git', 'fcitx-table-cn-wubi-pinyin','ctags', 'imagewriter']
		with mock.patch('os.system', lambda x: infos.append(x)):
			cr.install_software(plantform='opensuse', softs=softs)

		patts = ['sudo zypper in -y %s' % soft for soft in softs]
		self.assertTrue(infos)
		self.assertEqual(infos, patts)

	# @unittest.skip
	def test_install_pip_module(self):
		# softs = ['bpython']
		patts = ['sudo pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/', 
			'sudo pip install -i https://pypi.tuna.tsinghua.edu.cn/simple/ selenium']
		infos = []
		with mock.patch('os.system', lambda x: infos.append(x)):
			cr.install_pip_module(file='requirements.txt', softs=['selenium'])
		self.assertTrue(infos)
		self.assertEqual(infos, patts)

	# @unittest.skip
	def test_improved_bash(self):
		infos = []
		alias = {'test':'newtest'}
		patts = ['echo "alias test=\'newtest\'" >> ~/.bashrc', 'echo export PATH=~/bin:$PATH >> ~/.bashrc']
		with mock.patch('os.system', lambda x: infos.append(x)):
			cr.improved_bash(alias=alias, cmds=['export PATH=~/bin:$PATH'], filename='')
		
		self.assertTrue(infos)
		self.assertEqual(infos, patts)

	def test_add_repos(self):
		self.fail('to be implemented')


if __name__ == '__main__':
	print('starting test....')
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