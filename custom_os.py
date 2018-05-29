#!/usr/bin/python3
"""
Changing Repository from dowload.opensuse.org to mirrors.tuna.tsinghua.edu.cn/opensuse and 
install popular software.
Running only once on first running after system installed
"""
import os
import sys
import time
from urllib.request import urlopen
import json
import pwd
from socket import timeout

VAR_MAPPING = {
    "PIP_INDEX": '',
    "USER_NAME": '',
    "USER_HOME": '',
    "SUSE_VERSION": '',
    "FULL_SUSE_VERSION": '',
    "MIRROR_URL": '',
}


class CustomOS(object):
    """
    change repository to specified mirror
    """

    def __init__(self, platform, version, mirror_name, file_name='configs.json'):
        self.mirror_name = mirror_name
        self.config_file = file_name
        self.platform = platform
        self.version = version
        self.configs = {}
        self.get_config()
        self.get_var()
        self.check_config()

    def check_requirement(self):
        """
        check requirement to run this program
        """
        raise NotImplementedError

    def clear_repos(self):
        raise NotImplementedError

    def add_repo(self):
        """
        add repository
        """
        raise NotImplementedError

    def restart_network(self):
        raise NotImplementedError

    def install_software(self):
        """
        install software
        :return:
        """
        raise NotImplementedError

    @staticmethod
    def chk_permission():
        if os.geteuid() != 0:
            print('try: sudo python3 custom.py')
            exit(1)

    def get_config(self):
        try:
            self.configs = json.load(open(self.config_file))
        except json.JSONDecodeError:
            print('Can not read json file named %s, properly wrong json format' % self.config_file)
            sys.exit(1)

    def check_config(self):
        # check item in configs
        if not all([k in self.configs for k in ['common', 'bash']]):
            raise Exception('Can not find common or bash parameters in file named %s' % self.config_file)
        if self.platform not in self.configs:
            raise Exception('Not supported os named %s' % self.platform)
        # checking pypi, mirror name, pip module file name, host url
        m_pypi = self.mirror_name + '_pypi'
        common_item = ['host', 'pip_software', self.mirror_name, m_pypi]
        if not all([k in self.configs['common'] for k in common_item]):
            raise Exception('Can not find all "%s" in common in file named %s' % (common_item, self.config_file))
        self.chk_url(self.configs['common'][m_pypi])
        self.chk_url(self.configs['common'][self.mirror_name])
        self.chk_url(self.configs['common']['host'])
        req_file = self.configs['common']['pip_software']
        if not os.path.exists(req_file):
            raise Exception('Can not find file named %s' % req_file)

    def get_var(self):
        """
        get variable
        """
        index_name = self.mirror_name + "_pypi"
        VAR_MAPPING["PIP_INDEX"] = self.configs["common"][index_name]
        user_name, user_home = self.get_user_info()
        VAR_MAPPING["USER_NAME"] = user_name
        VAR_MAPPING["USER_HOME"] = user_home
        VAR_MAPPING["SUSE_VERSION"] = self.version
        VAR_MAPPING["FULL_SUSE_VERSION"] = 'openSUSE_Leap_%s' % self.version
        VAR_MAPPING["MIRROR_URL"] = self.configs["common"][self.mirror_name]

    @staticmethod
    def chk_url(url, time_out=30):
        try:
            urlopen(url, timeout=time_out).read()
        except timeout:
            raise Exception('Can not access %s' % url)   

    @staticmethod
    def get_user_info(uid=1000):
        user = pwd.getpwuid(uid)
        username = user.pw_name
        dir_name = user.pw_dir
        return username, dir_name

    @staticmethod
    def gen_cmd(cmd):
        """
        set var in cmd
        :param cmd:
        :return:
        """
        d = {}
        for k, v in VAR_MAPPING.items():
            if k in cmd:
                d[k] = v
        return cmd.format(**d)

    def get_hosts(self):
        """
        get host file to fight GFW
        :return:
        """
        html = urlopen(self.configs['common']['host'], timeout=20)
        with open('hosts', 'wb') as h:
            h.write(html.read())
        # copy hosts
        os.system('sudo cat ./hosts >> /etc/hosts')
        self.restart_network()

    def execute_cmd(self):
        if os.geteuid() == 0:
            c = self.configs['common']['su_cmd']
        else:
            c = self.configs['common']['normal_cmd']
        for cmd in c:
            os.system(self.gen_cmd(cmd))

    def write_bash(self):
        """
        write bash
        :return:
        """
        bash_path = os.path.join(VAR_MAPPING["USER_HOME"], '.bashrc')
        alias = self.configs['bash']['alias']
        cmd = self.configs['bash']['cmd']
        with open(bash_path, 'a') as bash:
            for alia in self.configs['bash']['alias']:
                c = "alias %s='%s'\n" % (alia, alias[alia])
                bash.write(self.gen_cmd(c))
            bash.write("\n".join(cmd))

    def install_py_module(self):
        """
        install pip module
        :return:
        """
        pip_index = VAR_MAPPING['PIP_INDEX']
        req_file = self.configs['common']['pip_software']
        os.system('sudo pip3 install -r %s -i %s' % (req_file, pip_index))


class Ubuntu(CustomOS):
    '''
    initializing ubuntn os
    '''
    def __init__(self, version, mirror_name, file_name='configs.json'):
        CustomOS.__init__(self, 'ubuntu', version, mirror_name, file_name)

    # def _chk_config(self):
    #     CustomOS._chk_config(self)
    #     to_be_check = self.configs[self.platform]['os'][self.version]
    #     if self.mirror_name not in to_be_check or not to_be_check[self.mirror_name]:
    #         raise Exception('Repository url is required for %s of %s' % (self.version, self.platform))
    #     self.chk_url(to_be_check[self.mirror_name])
    #     if not 'repos' in to_be_check or not to_be_check['repos']:
    #         raise Exception('Need source name in %s of %s\'s repos' % (self.version, self.platform))

    def clear_repos(self):
        source_path = '/etc/apt/sources.list'
        os.rename(source_path, source_path+'.bak')

    def add_repo(self):
        source_path = '/etc/apt/sources.list'
        sources = []
        url = self.configs[self.platform]['os'][self.version][self.mirror_name]
        for repo in self.configs[self.platform]['os'][self.version]['repos']:
            sources.append('deb %s %s' % (url, repo))
        with open(source_path, 'w') as f:
            f.write('\n'.join(sources))
        for repo in self.configs[self.platform]['os'][self.version]['custom_repos']:
            os.system(repo)
        os.system('sudo apt-get update')

    def install_software(self):
        software = self.configs[self.platform]['software']
        for soft in software:
            os.system('sudo apt-get -y install %s' % soft)


class Opensuse(CustomOS):
    """
    initializing openSUSE
    """
    def __init__(self, version, mirror_name, file_name='configs.json'):
        CustomOS.__init__(self, 'opensuse', version, mirror_name, file_name)
        self.check_requirement()

    def check_requirement(self):
        # check url in opensuse repo
        for repo in self.configs['opensuse']['repos']:
            url = self.gen_cmd(repo['url'])
            self.chk_url(url)
        self.chk_permission()

    def clear_repos(self):
        repo_dir = '/etc/zypp/repos.d/'
        repos = os.listdir(repo_dir)
        for repo in repos:
            os.unlink(os.path.join(repo_dir, repo))

    def add_repo(self):
        repos = self.configs[self.platform]['repos']
        custom_repos = self.configs[self.platform]['custom_repos']
        add_repo = 'sudo zypper --gpg-auto-import-keys addrepo --check --refresh --name "%s" %s "%s"'
        for repo in repos:
            url = self.gen_cmd(repo["url"])
            os.system(add_repo % (repo['name'], url, repo['name']))
        for repo in custom_repos:
            os.system(repo)

    def install_software(self, mode='laptop'):
        """
        install software
        :param mode:
        :return:
        """
        software = self.configs[self.platform]['software']
        for soft in software["dev"]:
            os.system('sudo zypper --gpg-auto-import-keys in -y %s' % soft.strip())
        if mode == 'server':
            return
        for soft in software["laptop"]:
            os.system('sudo zypper --gpg-auto-import-keys in -y %s' % soft.strip())

    def restart_network(self):
        os.system('sudo systemctl restart NetworkManager')
        time.sleep(10)


if __name__ == '__main__':
    with open('/etc/os-release') as f:
        lines = f.readlines()
    platform = ''
    for line in lines:
        tmp = line.strip().split('=')
        name = tmp[0]
        if name == "NAME":
            s = tmp[1].replace('"', '').lower()
            platform, _ = s.split()
            break

    if platform not in ['ubuntu', 'opensuse']:
        raise Exception('Unknown os %s' % platform)

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', help='mirror name, default is tuna mirror')
    parser.add_argument('-v', help='os version, like 16.04 for ubuntu, tumbleweed for opensuse')
    parser.add_argument('-s', action="store_false", default=False,
                        help="running script under server mode or not, default is not ")
    args, unknown = parser.parse_known_args()
    m = args.m or 'tuna'
    if m not in ['tuna', 'ustc']:
        raise Exception('Please add mirror name %s in config.json')
    if not args.v:
        print(parser.print_help())
        sys.exit(1)
    if args.s:
        mode = "laptop"
        print("under laptop mode")
    else:
        mode = "server"
        print("under server mode")
    print('checking config.json')
    if platform != 'opensuse':
        raise NotImplementedError("%s does not supported yet" % platform)
    myOS = Opensuse(args.v, m)
    print('clearing repository')
    myOS.clear_repos()
    print('getting host file')
    myOS.get_hosts()
    print('adding repository')
    myOS.add_repo()
    print('installing software')
    myOS.install_software(mode)
    print('installing pip module')
    myOS.install_py_module()
    print('writing file bashrc')
    myOS.write_bash()
    print('executing sudo cmd')
    myOS.execute_cmd()
    print("executing normal cmd")
    os.seteuid(1000)
    myOS.execute_cmd()
