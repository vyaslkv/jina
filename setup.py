import sys
from os import path

from setuptools import find_packages
from setuptools import setup
from setuptools.command.develop import develop
from setuptools.command.install import install

PY37 = 'py37'
PY38 = 'py38'

if sys.version_info >= (3, 8, 0):
    py_tag = PY38
elif sys.version_info >= (3, 7, 0):
    py_tag = PY37
else:
    raise OSError('Jina requires Python 3.7 and above, but yours is %s' % sys.version_info)

try:
    pkg_name = 'jina'
    libinfo_py = path.join(pkg_name, '__init__.py')
    libinfo_content = open(libinfo_py, 'r', encoding='utf8').readlines()
    version_line = [l.strip() for l in libinfo_content if l.startswith('__version__')][0]
    exec(version_line)  # gives __version__
except FileNotFoundError:
    __version__ = '0.0.0'

try:
    with open('README.md', encoding='utf8') as fp:
        _long_description = fp.read()
except FileNotFoundError:
    _long_description = ''

base_dep = [
    'numpy',
    'pyzmq>=17.1.0',
    'protobuf',
    'grpcio',
    'ruamel.yaml>=0.15.89',
]


def get_extra_requires(path, add_all=True):
    import re
    from collections import defaultdict
    try:
        with open(path) as fp:
            extra_deps = defaultdict(set)
            for k in fp:
                if k.strip() and not k.startswith('#'):
                    tags = set()
                    if ':' in k:
                        k, v = k.split(':')
                        tags.update(vv.strip() for vv in v.split(','))
                    tags.add(re.split('[<=>]', k)[0])
                    for t in tags:
                        extra_deps[t].add(k)
                    if PY37 not in tags and PY38 not in tags:
                        # no specific python version required
                        extra_deps[PY37].add(k)
                        extra_deps[PY38].add(k)

            # add tag `all` at the end
            if add_all:
                extra_deps['all'] = set(vv for v in extra_deps.values() for vv in v)
                extra_deps['match-py-ver'] = extra_deps[py_tag]

        return extra_deps
    except FileNotFoundError:
        return {}


def register_ac():
    from pathlib import Path
    import os
    from pkg_resources import resource_stream

    home = str(Path.home())
    _check = [{'sh': os.path.join(home, '.zshrc'),
               'ac': resource_stream('jina', '/'.join(('resources', 'completions', 'jina.zsh'))).read()},
              {'sh': os.path.join(home, '.bashrc'),
               'ac': resource_stream('jina', '/'.join(('resources', 'completions', 'jina.bash'))).read()},
              {'sh': os.path.join(home, '.config', 'fish', 'config.fish'),
               'ac': resource_stream('jina', '/'.join(('resources', 'completions', 'jina.fish'))).read()}]

    def add_ac(f):
        if os.path.exists(f['sh']):
            # zsh installed:
            already_in = False
            with open(f['sh']) as fp:
                for v in fp:
                    if '# Jina CLI Autocomplete' in v:
                        already_in = True
                        break
            if not already_in:
                with open(f['sh'], 'a') as fp:
                    fp.write(f['ac'].decode())

    try:
        for k in _check:
            add_ac(k)
    except Exception:
        pass


class PostDevelopCommand(develop):
    """Post-installation for development mode."""

    def run(self):
        develop.run(self)
        register_ac()


class PostInstallCommand(install):
    """Post-installation for installation mode."""

    def run(self):
        install.run(self)
        register_ac()


setup(
    name=pkg_name,
    packages=find_packages(),
    version=__version__,
    include_package_data=True,
    description='Jina is the cloud-native neural search solution powered by the state-of-the-art AI and deep learning',
    author='Jina Dev Team',
    author_email='dev-team@jina.ai',
    license='Apache 2.0',
    url='https://opensource.jina.ai',
    download_url='https://github.com/jina-ai/jina/tags',
    long_description=_long_description,
    long_description_content_type='text/markdown',
    zip_safe=False,
    setup_requires=[
        'setuptools>=18.0',
    ],
    install_requires=base_dep,
    extras_require=get_extra_requires('extra-requirements.txt'),
    entry_points={
        'console_scripts': ['jina=jina.main:main'],
    },
    cmdclass={
        'develop': PostDevelopCommand,
        'install': PostInstallCommand,
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Unix Shell',
        'Environment :: Console',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Topic :: Database :: Database Engines/Servers',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Internet :: WWW/HTTP :: Indexing/Search',
        'Topic :: Scientific/Engineering :: Image Recognition',
        'Topic :: Multimedia :: Video',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Mathematics',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords='jina cloud-native semantic query search index elastic neural-network encoding '
             'embedding serving docker container image video audio deep-learning',
)
