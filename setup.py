from setuptools import setup, find_packages
from setuptools.command.install import install
import os

class PostInstallCommand(install):
    """Post-installation for installation mode."""
    def run(self):        
        install.run(self)
        from tomo2bm.auto_complete import create_complete_scan
        import pathlib
        fname = os.path.expanduser("~")+'/complete_tomo.sh'        
        create_complete_scan.run(fname)
        print('For autocomplete please run: \n\n $ source '+ fname +'\n')
setup(
    name='tomo2bm',
    version=open('VERSION').read().strip(),
    #version=__version__,
    author='Francesco De Carlo',
    author_email='decarlof@gmail.com',
    url='https://github.com/decarlof/2bm-tomo',
    packages=find_packages(),
    include_package_data = True,
    scripts=['bin/tomo'],
    description='cli to run tomo scans at 2-bm',
    zip_safe=False,
    cmdclass={'install': PostInstallCommand}
)