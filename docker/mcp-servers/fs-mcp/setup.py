import os

from setuptools import setup, find_packages

setup(
    name='fs-mcp',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[],
    entry_points={
        'console_scripts': [
            'fs-mcp=server:main',
        ],
    },
)
