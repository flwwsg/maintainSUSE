#!/usr/bin/python3
"""
Changing Repository from dowload.opensuse.org to mirrors.tuna.tsinghua.edu.cn/opensuse and 
install popular software.
Running only once on first running after system installed
"""
import os, sys
import time

# from urllib.request import urlopen
# import grp
# import getpass

# euid = os.geteuid()
# if euid != 0:
# 	print('try: sudo python3 changeRepo.py')
# 	exit(1)

# pattern = 'http://download.opensuse.org'
# replace = 'https://mirrors.tuna.tsinghua.edu.cn/opensuse'
# softwares = ['chromium', 'git', 'fcitx-table-cn-wubi-pinyin', 'ctags',
# 	'virtualbox', 'python3-tk', 'python3-virtualenv', 'docker', 'python3-devel', 'python3-curses', 'htop', 'redshift'
# 	' -t pattern devel_basis', 'imagewriter',]
# # 'sudo zypper install -t pattern devel_basis'  build essential
# ignore = ['repo-debug', 'repo-debug-non-oss', 'repo-debug-update',
# 			'repo-debug-update-non-oss','repo-source', 'repo-source-non-oss']
# groups = ['docker', 'vboxusers']

# # reserve = ['repo-update','repo-update-non-oss']
# reserve = list()
# addrepo = 'sudo zypper addrepo --check --refresh --name "%s" %s "%s"'
# remove = 'sudo zypper removerepo %s'
# packman = 'https://mirrors.tuna.tsinghua.edu.cn/packman/suse/%s/'

# hfile = 'hosts'

# html = urlopen('https://coding.net/u/scaffrey/p/hosts/git/raw/master/hosts')
# with open(hfile,'wb') as f:
# 	f.write(html.read()) 
# #copy hosts
# os.system('sudo cat ./hosts >> /etc/hosts')
# os.system('sudo systemctl restart NetworkManager')
# time.sleep(10)
# #packman
# versions = os.popen('cat /etc/os-release').readlines()
# for line in versions:
# 	tmp = line.strip().replace('"','').split('=')
# 	if tmp[0] == 'PRETTY_NAME':
# 		version = tmp[1].replace(' ','_')
# 		break
# repos = dict()
# repos['tuna-packman'] = packman % version

# outs = os.popen('zypper repos -d').readlines()
# for line in outs[2:]:
# 	tmp = line.split('|')
# 	alias = tmp[1].strip()
# 	url = tmp[8]
# 	os.system(remove % alias)
# 	if alias in ignore or not alias:
# 		continue
# 	else:
# 		if alias in reserve:
# 			repos[alias] = url
# 		turl = url.replace(pattern, replace)
# 		tname = alias if alias.startswith('tuna-') else 'tuna-'+alias
# 		repos[tname] = turl	

# for name, url in repos.items():
# 	os.system(addrepo % (name, url, name))

# # zypper refresh
# os.system('sudo zypper refresh')

# for software in softwares:
# 	os.system('sudo zypper in -y %s' % software)

# #configure git
# os.system('git config --global user.email "2319406132@qq.com"')
# os.system("git config --global user.name 'flwwsg'")

# #pip pakage
# pkgs = ['bpython']

# for pkg in pkgs:
#     os.system('sudo pip -i https://pypi.tuna.tsinghua.edu.cn/simple/ install %s'%pkg)

# # add groups 
# uname = getpass.getuser()
# for group in groups:
#     os.system('sudo usermod -aG %s %s' % group, uname)
# =======
import configparser

# from urllib.request import urlopen

# OSINFO = {'id':'plantform', 'pretty_name':'version'}
SUPPORTEDOS = ['opensuse','tumbleweed']

def get_config(file='configs'):
	config = configparser.ConfigParser()
	config.read_file(open(file))
	return config

config = get_config()

def changerepo(plantform='opensuse',mirrorname='tuna'):
	"""change software repository to mirror site in china"""
	mirrorurl = config['repourl'][mirrorname]+plantform
	repos = config[plantform]['repos'].split()
	reserved = config[plantform].get('reserved','').split()
	default_url = 'http://download.opensuse.org'
	addrepo = 'sudo zypper addrepo --check --refresh --name "%s" %s "%s"'
	removerepo = 'sudo zypper removerepo %s'

	outs = os.popen('zypper repos -d').readlines()
	newrepos = {}
	for line in outs:
		tmp = line.split('|')
		if len(tmp) <8 or tmp[1].strip() == 'Alias':
			continue

		alias = tmp[1].strip()
		if alias not in reserved:
			os.system(removerepo % alias)
		if alias not in repos:
			continue
		url = tmp[8]
		turl = url.replace(default_url, mirrorurl)
		tname = alias if alias.startswith(mirrorname+'-') else mirrorname+'-'+alias
		newrepos[tname] = turl	

	for name, url in newrepos.items():
		os.system(addrepo % (name, url, name))

def install_software(plantform='opensuse', softs=[]):
	for soft in softs:
		os.system('sudo zypper in -y %s' % soft)


def install_pip_module(file='', softs=[]):
	if file:
		os.system('sudo pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/')
	if softs:
		for soft in softs:
			os.system('sudo pip install -i https://pypi.tuna.tsinghua.edu.cn/simple/ %s' % soft)

def improved_bash(alias={}, cmds=[], filename=''):
	if not filename:
		filename = '~/.bashrc'
	for cmd, alia in alias.items():
		os.system('echo "alias %s=\'%s\'" >> %s' % (cmd, alia, filename))
	for cmd in cmds:
		os.system('echo %s >> %s' % (cmd, filename))

# class ChangeRepo(object):
# 	"""change repository to chinese mirror"""
# 	def __init__(self, plantform='',config='configs'):
# 		self._chk_permission()
# 		if not plantform:
# 			self._get_plantform()

# 	def _get_plantform(self):
# 		# versions = os.popen('cat /etc/os-release').readlines()
# 		# for line in versions:
# 		# 	tmp = line.strip().replace('"','').split('=')
# 		# 	if tmp[0].lower() in OSINFO:
# 		# 		setattr(self, plantform, tmp[1])
# 				# if tmp[0] == 'PRETTY_NAME':
# 				# 	version = tmp[1].replace(' ','_')
# 				# 	break
# 		self.plantform = 'opensuse'

# 	def _chk_permission(self):
# 		euid = os.geteuid()
# 		if euid != 0:
# 			print('try: sudo python3 changeRepo.py')
# 			exit(1)


# euid = os.geteuid()
# if euid != 0:
# 	print('try: sudo python3 changeRepo.py')
# 	exit(1)

# pattern = 'http://download.opensuse.org'
# replace = 'https://mirrors.tuna.tsinghua.edu.cn/opensuse'
# softwares = ['git', 'fcitx-table-cn-wubi-pinyin','ctags' , 'virtualbox', 
# 			'python3-tk','python3-virtualenv' , 'docker', 'python3-devel', ' -t pattern devel_basis',
# 			'imagewriter',]
# 			 # 'sudo zypper install -t pattern devel_basis'  build essential
# ignore = ['repo-debug', 'repo-debug-non-oss', 'repo-debug-update',
# 			'repo-debug-update-non-oss','repo-source', 'repo-source-non-oss']
# groups = ['docker', 'vboxusers']

# # reserve = ['repo-update','repo-update-non-oss']
# reserve = list()
# addrepo = 'sudo zypper addrepo --check --refresh --name "%s" %s "%s"'
# remove = 'sudo zypper removerepo %s'
# packman = 'https://mirrors.tuna.tsinghua.edu.cn/packman/suse/%s/'

# hfile = 'hosts'

# html = urlopen('https://raw.githubusercontent.com/flwwsg/hosts/master/hosts')
# with open(hfile,'wb') as f:
# 	f.write(html.read()) 
# #copy hosts
# os.system('sudo cat ./hosts >> /etc/hosts')
# os.system('sudo systemctl restart NetworkManager')
# time.sleep(10)
# #packman
# versions = os.popen('cat /etc/os-release').readlines()
# for line in versions:
# 	tmp = line.strip().replace('"','').split('=')
# 	if tmp[0] == 'PRETTY_NAME':
# 		version = tmp[1].replace(' ','_')
# 		break
# repos = dict()
# repos['tuna-packman'] = packman % version

# outs = os.popen('zypper repos -d').readlines()
# for line in outs[2:]:
# 	tmp = line.split('|')
# 	alias = tmp[1].strip()
# 	url = tmp[8]
# 	os.system(remove % alias)
# 	if alias in ignore or not alias:
# 		continue
# 	else:
# 		if alias in reserve:
# 			repos[alias] = url
# 		turl = url.replace(pattern, replace)
# 		tname = alias if alias.startswith('tuna-') else 'tuna-'+alias
# 		repos[tname] = turl	

# for name, url in repos.items():
# 	os.system(addrepo % (name, url, name))

# # zypper refresh
# os.system('sudo zypper refresh')

# for software in softwares:
# 	os.system('sudo zypper in -y %s' % software)

# #configure git
# os.system('git config --global user.email "2319406132@qq.com"')
# os.system("git config --global user.name 'flwwsg'")

# # add groups 
# for group in groups:
# 	os.system('sudo usermod -aG %s lblue' % group)
# 	os.system('sudo usermod -aG %s dev' % group)
# # sudo usermod -aG groupName userName
# # sudo usermod -aG vboxusers lblue

# def gen_bashrc():
# 	alias = {'grep':'grep -E --color=auto', 
# 		# 'pip':'pip -i https://pypi.tuna.tsinghua.edu.cn/simple/'
# 		}
# # =======
# from urllib.request import urlopen
# import grp
# import getpass

# euid = os.geteuid()
# if euid != 0:
# 	print('try: sudo python3 changeRepo.py')
# 	exit(1)

# pattern = 'http://download.opensuse.org'
# replace = 'https://mirrors.tuna.tsinghua.edu.cn/opensuse'
# softwares = ['chromium', 'git', 'fcitx-table-cn-wubi-pinyin', 'ctags',
# 	'virtualbox', 'python3-tk', 'python3-virtualenv', 'docker', 'python3-devel', 'python3-curses',
# 	' -t pattern devel_basis', 'imagewriter',]
# # 'sudo zypper install -t pattern devel_basis'  build essential
# ignore = ['repo-debug', 'repo-debug-non-oss', 'repo-debug-update',
# 			'repo-debug-update-non-oss','repo-source', 'repo-source-non-oss']
# groups = ['docker', 'vboxusers']

# # reserve = ['repo-update','repo-update-non-oss']
# reserve = list()
# addrepo = 'sudo zypper addrepo --check --refresh --name "%s" %s "%s"'
# remove = 'sudo zypper removerepo %s'
# packman = 'https://mirrors.tuna.tsinghua.edu.cn/packman/suse/%s/'

# hfile = 'hosts'

# html = urlopen('https://coding.net/u/scaffrey/p/hosts/git/raw/master/hosts')
# with open(hfile,'wb') as f:
# 	f.write(html.read()) 
# #copy hosts
# os.system('sudo cat ./hosts >> /etc/hosts')
# os.system('sudo systemctl restart NetworkManager')
# time.sleep(10)
# #packman
# versions = os.popen('cat /etc/os-release').readlines()
# for line in versions:
# 	tmp = line.strip().replace('"','').split('=')
# 	if tmp[0] == 'PRETTY_NAME':
# 		version = tmp[1].replace(' ','_')
# 		break
# repos = dict()
# repos['tuna-packman'] = packman % version

# outs = os.popen('zypper repos -d').readlines()
# for line in outs[2:]:
# 	tmp = line.split('|')
# 	alias = tmp[1].strip()
# 	url = tmp[8]
# 	os.system(remove % alias)
# 	if alias in ignore or not alias:
# 		continue
# 	else:
# 		if alias in reserve:
# 			repos[alias] = url
# 		turl = url.replace(pattern, replace)
# 		tname = alias if alias.startswith('tuna-') else 'tuna-'+alias
# 		repos[tname] = turl	

# for name, url in repos.items():
# 	os.system(addrepo % (name, url, name))

# # zypper refresh
# os.system('sudo zypper refresh')

# for software in softwares:
# 	os.system('sudo zypper in -y %s' % software)

# #configure git
# os.system('git config --global user.email "2319406132@qq.com"')
# os.system("git config --global user.name 'flwwsg'")

# #pip pakage
# pkgs = ['bpython']

# for pkg in pkgs:
#     os.system('sudo pip -i https://pypi.tuna.tsinghua.edu.cn/simple/ install %s'%pkg)

# # add groups 
# uname = getpass.getuser()
# for group in groups:
#     os.system('sudo usermod -aG %s %s' % group, uname)
# >>>>>>> ea81b6f82fce8992cf94726737a40bee764127ce
		
# # sudo usermod -aG groupName userName
# # sudo usermod -aG vboxusers lblue


# def gen_bashrc():
#     alias = {'grep':'grep -E --color=auto', 
# 		# 'pip':'pip -i https://pypi.tuna.tsinghua.edu.cn/simple/'
# 		}
# # https://download.sublimetext.com/rpm/stable/x86_64/sublime-text.repo sublime repo
# # >>>>>>> 0ffdd170f0f0ae648aa490c382a9a5cfc0117d05
