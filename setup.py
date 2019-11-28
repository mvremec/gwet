from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='gwet',
    version='0.1',
    packages=[''],
    url='https://github.com/matevzvremec/gwet',
    license='GNU General public version 3.0',
    author='Matevz Vremec',
    author_email='matevz.vremec@uni-graz.at',
    long_description=long_description,
    description='Gwet - soil water balance model'
    install_requires=['numpy>=1.15', 'matplotlib>=2.0', 'pandas>=0.23',
                      'scipy>=1.1']
)
