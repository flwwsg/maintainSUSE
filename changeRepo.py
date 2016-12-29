#!/usr/bin/python3
import os, sys

pattern = 'http://download.opensuse.org'
replace = 'https://mirrors.tuna.tsinghua.edu.cn'
ignore = ['repo-debug', 'repo-debug-non-oss', 'repo-debug-update',
			'repo-debug-update-non-oss','repo-source', 'repo-source-non-oss']
reserve = ['repo-update','repo-update-non-oss']
cmd = 'zypper addrepo --check --refresh --name "%s" %s "%s"'
remove = 'zypper removerepo %s'
packman = 'https://mirrors.tuna.tsinghua.edu.cn/packman/suse/%s/'

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
	if alias in ignore:
		continue
	else:
		if alias in reserve:
			repos[alias] = url
		turl = url.replace(pattern, replace)
		tname = alias if alias.startswith('tuna-') else 'tuna-'+alias
		repos[tname] = turl	

for name, url in repos.items():
	os.system(cmd % (name, url, name))