"""
common file for maintaining opensuse
"""
import os


USER = os.getlogin() 
HOME = '/home/%s' % USER

# folder listed in dirfilters will be unchanged
dirfilters = {'dev':['lims']}

#Changing file mod to 775 for sharing .
#replace space (' ') in path to ('\ ') avoid misstake in bash
def changeMod(mod=775, directories=None):
	chmod = 'sudo chmod -R %s %s'
	if not directories:
		directories = ['dev', 'django18', 'bin', 'VirtualBox VMs','Documents', 'Downloads', 'Music']
	for folder in directories:
		path = os.path.join(HOME, folder)
		if not os.path.exists(path):
			continue

		if folder in dirfilters.keys():
			subdirs = os.listdir(path)
			remain = set(subdirs) - set(dirfilters[folder])
			remain = list(remain)
			# print(remain)
			for ipath in remain:
				path = os.path.join(path, ipath)
				if not os.path.exists(path):
					continue
				path = path.replace(' ','\ ')
				cmd = chmod % (mod, path)
				os.system(cmd)
				# print(cmd)
		else:	
			path = path.replace(' ','\ ')
			cmd = chmod % (mod, path)
			os.system(cmd)
			# print(cmd)

if __name__ == '__main__':
	changeMod()
