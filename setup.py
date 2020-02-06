from setuptools import setup, find_packages

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
)