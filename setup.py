from setuptools import setup
from os import path


here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='dataclass-abc',
    version='0.0.8',
    description='Library that lets you define abstract properties for dataclasses.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/MichaelSchneeberger/dataclass-abc',
    author='Michael Schneeberger',
    author_email='michael.schneeb@outlook.com',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.11',
    ],
    keywords='dataclass-abc abstract abc property',
    packages=['dataclassabc'],
    python_requires='>=3.10',
)
