#!/usr/bin/env python

"""
NottReal — An application for running Wizard of Oz studies with a
simulated voice user interface.
"""

from setuptools import setup, find_packages

setup(
    name='NottReal',
    version='1.0.0',
    description=('An application for running Wizard of Oz studies with '
        'a simulated voice user interface.'),
    url='http://github.com/mporcheron/nottreal/',
    author='Martin Porcheron',
    author_email='martin+nottreal@porcheron.uk',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3 :: Only'],
    keywords='voice user interfaces vuis wizard of oz woz',
    package_dir={'': 'src'}, 
    packages=find_packages(where='src'), 
    python_requires='>=3.5, <4',
    install_requires=['numpy','python-gettext', 'pyaudio', 'PySide2','sounddevice'],
    package_data={
        'sample': ['cfg_dist/categories.tsv',
            'cfg_dist/log.tsv',
            'cfg_dist/loading.tsv',
            'cfg_dist/messages.tsv',
            'cfg_dist/settings.cfg']
    },
    entry_points={
        'console_scripts': [
            'run = nottreal:main',
        ],
    }
)
    
