from setuptools import setup, find_packages

setup(
    name='libgen',
    version='0.1',
    license='MIT',
    author='Adolfo Silva',
    author_email='code@adolfosilva.org',
    url='https://github.com/adolfosilva/libgen.py',
    description='A script to download books from gen.lib.rus.ec',
    package_dir={'': 'libgen'},
    packages=find_packages('libgen'),
    scripts=['bin/libgen.py'],
    tests_requires=['pytest']
)
