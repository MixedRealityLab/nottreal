#!/usr/bin/env python

"""
NottReal — An application for running Wizard of Oz studies with a
simulated voice user interface.
"""

from setuptools import setup, find_packages

setup(
    name='NottReal',
    version='1.0.1',
    description='An application for running Wizard of Oz studies with '
                'a simulated voice user interface.',
    url='http://github.com/mixedrealitylab/nottreal/',
    author='Martin Porcheron',
    author_email='martin+nottreal@porcheron.uk',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3 :: Only'],
    keywords='voice user interfaces vuis wizard of oz woz',
    package_dir={'': 'nottreal'},
    packages=find_packages(where='nottreal'),
    python_requires='>=3.5, <3.8',
    install_requires=[
        'numpy',
        'python-gettext',
        'pyaudio',
        'PySide2',
        'SpeechRecognition'],
    package_data={
        'sample': [
            'data/note.txt',
            'dist.nrc/categories.tsv',
            'dist.nrc/log.tsv',
            'dist.nrc/loading.tsv',
            'dist.nrc/messages.tsv',
            'dist.nrc/settings.cfg']
    },
    entry_points={
        'console_scripts': [
            'run = nottreal:main',
        ],
    }
)
