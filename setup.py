from setuptools import setup
from os import path


here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='dataclass-abc',
    version='0.0.1',
    description='Library that lets you define abstract properties in dataclasses.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/pypa/sampleproject',
    author='Michael Schneeberger',
    author_email='michael.schneeb@outlook.com',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    keywords='dataclass abstract abc property',
    packages=['dataclass_abc'],
    python_requires='>=3.7',
)
