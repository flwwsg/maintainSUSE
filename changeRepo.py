#!/usr/bin/python3
"""
Changing Repository from dowload.opensuse.org to mirrors.tuna.tsinghua.edu.cn/opensuse and 
install popular software.
Running only once on first running after system installed
"""
import os, sys
import time
from urllib.request import urlopen

euid = os.geteuid()
if euid != 0:
	print('try: sudo python3 changeRepo.py')
	exit(1)

pattern = 'http://download.opensuse.org'
replace = 'https://mirrors.tuna.tsinghua.edu.cn/opensuse'
softwares = ['chromium','gcc5', 'gcc5-c++','git', 'fcitx-table-cn-wubi-pinyin','ctags' , 'virtualbox', 
			'python3-tk','python3-virtualenv' , 'docker', 'python3-devel', ' -t pattern devel_basis',
			'imagewriter',]
			 # 'sudo zypper install -t pattern devel_basis'  build essential
ignore = ['repo-debug', 'repo-debug-non-oss', 'repo-debug-update',
			'repo-debug-update-non-oss','repo-source', 'repo-source-non-oss']
groups = ['docker', 'vboxusers']

# reserve = ['repo-update','repo-update-non-oss']
reserve = list()
addrepo = 'sudo zypper addrepo --check --refresh --name "%s" %s "%s"'
remove = 'sudo zypper removerepo %s'
packman = 'https://mirrors.tuna.tsinghua.edu.cn/packman/suse/%s/'

hfile = 'hosts'

html = urlopen('https://coding.net/u/scaffrey/p/hosts/git/raw/master/hosts')
with open(hfile,'wb') as f:
	f.write(html.read()) 
#copy hosts
os.system('sudo cat ./hosts >> /etc/hosts')
os.system('sudo systemctl restart NetworkManager')
time.sleep(10)
#packman
versions = os.popen('cat /etc/os-release').readlines()
for line in versions:
	tmp = line.strip().replace('"','').split('=')
	if tmp[0] == 'PRETTY_NAME':
		version = tmp[1].replace(' ','_')
		break
repos = dict()
repos['tuna-packman'] = packman % version

outs = os.popen('zypper repos -d').readlines()
for line in outs[2:]:
	tmp = line.split('|')
	alias = tmp[1].strip()
	url = tmp[8]
	os.system(remove % alias)
	if alias in ignore or not alias:
		continue
	else:
		if alias in reserve:
			repos[alias] = url
		turl = url.replace(pattern, replace)
		tname = alias if alias.startswith('tuna-') else 'tuna-'+alias
		repos[tname] = turl	

for name, url in repos.items():
	os.system(addrepo % (name, url, name))

# zypper refresh
os.system('sudo zypper refresh')

for software in softwares:
	os.system('sudo zypper in -y %s' % software)

#configure git
os.system('git config --global user.email "2319406132@qq.com"')
os.system("git config --global user.name 'flwwsg'")

# add groups 
for group in groups:
	os.system('sudo usermod -aG %s lblue' % group)
	os.system('sudo usermod -aG %s dev' % group)
# sudo usermod -aG groupName userName
# sudo usermod -aG vboxusers lblue

def gen_bashrc():
	alias = {'grep':'grep -E --color=auto', 
		# 'pip':'pip -i https://pypi.tuna.tsinghua.edu.cn/simple/'
		}
