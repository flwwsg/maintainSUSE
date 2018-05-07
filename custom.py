#!/usr/bin/python3
"""
Changing Repository from dowload.opensuse.org to mirrors.tuna.tsinghua.edu.cn/opensuse and 
install popular software.
Running only once on first running after system installed
"""
import os
import sys
import time
import configparser
from urllib.request import urlopen
import json
import pwd
from socket import timeout


VAR_MAPPING = {
    'PIPINDEX': 'get_var_pipindex',
    'USERNAME': 'get_var_username',
}

class CustomOS(object):
    """change repository to chinese mirror"""

    def __init__(self, plantform, version, mirror_name, file_name='configs.json'):
        self.mirror_name = mirror_name
        self.config_file = file_name
        self.plantform = plantform
        self.version = version
        self.check_prerequirements()
        
    def check_prerequirements(self):
        '''
        check requirement to run this program
        '''
        self._chk_permission()
        self._get_config()
        self._chk_config()
        self.get_var()

    def _chk_permission(self):
        euid = os.geteuid()
        if euid != 0:
            print('try: sudo python3 custom.py')
            exit(1)

    def _get_config(self):
        try:
            self.configs = json.load(open(self.config_file))
        except Exception:
            print('Can not read json file named %s, properly wrong json formate' % self.config_file)
            sys.exit(1)

    def _chk_config(self):
        '''
        checking parameters specified in configs
        '''
        # checking common
        common_item = ['pypi', 'host', 'pip_software', self.mirror_name]
        if not all([k in self.configs['common'] for k in ['pypi', 'host', 'pip_software', self.mirror_name]]):
            raise Exception('Can not find all "%s" in common in file named %s' % (common_item, self.config_file))

        if 'pypi' not in self.configs['common']:
            raise Exception('Can not find pypi item in common dictory') 
        for url in self.configs['common']['pypi']:
            self.chk_url(url)
        req_file = self.configs['common']['pip_software']
        if not os.path.exists(req_file):
            raise Exception('Can not find file named %s' % req_file)
        mirror_url = self.configs['common'][self.mirror_name]
        self.chk_url(mirror_url)
        host_url = self.configs['common']['host']
        self.chk_url(host_url)
        if self.plantform not in self.configs:
            raise Exception('Not supported os named %s' % self.plantform)
        if self.version not in self.configs[self.plantform]['os']:
            raise Exception('Not supported version %s of %s' % (self.version, self.plantform))
        if not all([k in self.configs for k in ['common', 'bash']]):
            raise Exception('Can not find common or bash parameters in file named %s' % self.config_file)

    def __getattribute__(self, item):
        if item[:8] == 'get_var_' and hasattr(self, item[8:]):
            return getattr(self, item[8:])
        return object.__getattribute__(self, item)

    @staticmethod
    def clear_repos():
        repo_dir = '/etc/zypp/repos.d/'
        repos = os.listdir(repo_dir)
        for repo in repos:
            os.unlink(os.path.join(repo_dir, repo))

    @staticmethod
    def chk_url(url, time_out=30):
        try:
            resp = urlopen(url, timeout=time_out).read()
        except timeout:
            raise Exception('Can not access %s' % url)   

    @staticmethod
    def get_user_info(uid=1000):
        # try:
        #     infos = pwd.getpwuid(uid)
        # except Exception:
        #     return '', ''
        infos = pwd.getpwuid(uid)
        username = infos.pw_name
        dirname = infos.pw_dir
        return username, dirname

    def get_var(self):
        '''
        get variable
        '''
        index = 0 if self.mirror_name == "tuna" else 1
        self.pipindex = self.configs['common']['pypi'][index]
        self.username, self.userhome = self.get_user_info()

    def get_cmd_var(self, cmd):
        '''
        get variable in cmd
        '''
        env = self.configs['common']['env_var']
        var_map = {}
        for var in env:
            if var in cmd:
                attr = getattr(self, VAR_MAPPING[var])
                if callable(attr):
                    attr = attr()
                var_map[var] = attr
        return var_map
                
    def add_repo(self):
        '''
        add repository
        '''
        raise NotImplementedError

    def get_hosts(self):
        '''
        get host file to fight GFW
        '''
        html = urlopen(self.configs['common']['host'], timeout=20)
        with open('hosts', 'wb') as f:
            f.write(html.read())
        # copy hosts
        os.system('sudo cat ./hosts >> /etc/hosts')
        os.system('sudo systemctl restart NetworkManager')
        time.sleep(10)

    def excute_cmd(self):
        cmds = self.configs['common']['cmd']
        for cmd in cmds:
            k = self.get_cmd_var(cmd)
            os.system(cmd.format(**k))

    def write_bashrc(self):
        '''
        write bashrc
        '''
        bashrc = os.path.join(self.userhome, '.bashrc')
        alias = self.configs['bash']['alias']
        exports= self.configs['bash']['export']
        cmds = self.configs['bash']['cmd']
        with open(bashrc, 'a') as f:
            for alia in self.configs['bash']['alias']:
                var_map = self.get_cmd_var(alias[alia])
                f.write('alias %s=\'%s\'\n' % (alia, alias[alia].format(**var_map)))
            for export in exports:
                f.write('export %s\n' % export)
            for cmd in cmds:
                f.write(cmd+'\n')
        os.system('source '+bashrc)


    def install_software(self):
        '''
        install software
        '''
        raise NotImplementedError

    def install_py_module(self):
        '''
        install pip module
        '''
        pipindex = self.configs['common']['pypi'][0]
        req_file = self.configs['common']['pip_software']
        os.system('sudo pip3 install -r %s -i %s' % (req_file, pipindex))


class Ubuntu(CustomOS):
    '''
    initializing ubuntn os
    '''
    def __init__(self, version, mirror_name, file_name='configs.json'):
        CustomOS.__init__(self, 'ubuntu', version, mirror_name, file_name)

    def _chk_config(self):
        CustomOS._chk_config(self)
        to_be_check = self.configs[self.plantform]['os'][self.version]
        if self.mirror_name not in to_be_check or not to_be_check[self.mirror_name]:
            raise Exception('Repository url is required for %s of %s' % (self.version, self.plantform))
        self.chk_url(to_be_check[self.mirror_name])
        if not 'repos' in to_be_check or not to_be_check['repos']:
            raise Exception('Need source name in %s of %s\'s repos' % (self.version, self.plantform))

    def clear_repos(self):
        source_path = '/etc/apt/sources.list'
        os.rename(source_path, source_path+'.bak')

    def add_repo(self):
        source_path = '/etc/apt/sources.list'
        sources = []
        url = self.configs[self.plantform]['os'][self.version][self.mirror_name]
        for repo in self.configs[self.plantform]['os'][self.version]['repos']:
            sources.append('deb %s %s' % (url, repo))
        with open(source_path, 'w') as f:
            f.write('\n'.join(sources))
        for repo in self.configs[self.plantform]['os'][self.version]['custom_repos']:
            os.system(repo)
        os.system('sudo apt-get update')
    
    def install_software(self):
        software = self.configs[self.plantform]['software']
        for soft in software:
            os.system('sudo apt-get -y install %s' % soft)
        
class Opensuse(CustomOS):
    '''
    initializing opensuse
    '''
    def __init__(self, version, mirror_name, file_name='configs.json'):
        CustomOS.__init__(self, 'opensuse', version, mirror_name, file_name)

    def _chk_config(self):
        # checking repository
        CustomOS._chk_config(self)
        for repo in self.configs[self.plantform]['os'][self.version]['repos']:
            url = repo['url']
            self.chk_url(url)

    def clear_repos(self):
        repo_dir = '/etc/zypp/repos.d/'
        repos = os.listdir(repo_dir)
        for repo in repos:
            os.unlink(os.path.join(repo_dir, repo))

    def add_repo(self):
        repos = self.configs[self.plantform]['os'][self.version]['repos']
        custom_repos = self.configs[self.plantform]['custom_repos']
        addrepo = 'sudo zypper --non-interactive --no-gpg-checks --gpg-auto-import-keys addrepo --check --refresh --name "%s" %s "%s"'
        for repo in repos:
            os.system(addrepo % (repo['name'], repo['url'], repo['name']))
        for crepo in custom_repos:
            os.system(crepo)

    def install_software(self):
        '''
        install software
        '''
        software = self.configs[self.plantform]['software']
        for soft in software:
            os.system('sudo zypper in -y %s' % soft.strip())

# #configure git
# os.system('git config --global user.email "2319406132@qq.com"')
# os.system("git config --global user.name 'flwwsg'")


if __name__ == '__main__':
    with open('/etc/os-release') as f:
        infos = f.readlines()
    plantform = ''
    for line in infos:
        tmp = line.strip().split('=')
        name = tmp[0]
        if name == 'ID':
            plantform = tmp[1].replace('"', '').lower()
            break

    if plantform not in ['ubuntu', 'opensuse']:
        raise Exception('Unknown os %s' % plantform)

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', help='mirror name, default is tuna mirror')
    parser.add_argument('-v', help='os version, like 16.04 for ubuntu, tumbleweed for opensuse')
    args, unknown = parser.parse_known_args()
    m = args.m or 'tuna'
    if m not in ['tuna', 'ustc']:
        raise Exception('Please add mirror name %s in config.json')
    if not args.v:
        print(parser.print_help())
        sys.exit(1)
    print('checking config.json')
    if plantform == 'ubuntu':
        cos = Ubuntu(args.v, m)
    elif plantform == 'opensuse':
        cos = Opensuse(args.v, m)
    print('clearing repository')
    cos.clear_repos()
    print('geting host file')
    cos.get_hosts()
    print('adding repository')
    cos.add_repo()
    print('installing software')
    cos.install_software()
    print('installing pip module')
    cos.install_py_module()
    print('writing bashrc')
    cos.write_bashrc()
    print('excuting cmd')
    cos.excute_cmd()
    