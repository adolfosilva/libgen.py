from setuptools import setup

setup(
    name='libgen',
    version='0.1',
    license='MIT',
    author='Adolfo Silva',
    author_email='code@adolfosilva.org',
    url='https://github.com/adolfosilva/libgen.py',
    description='A script to download books from gen.lib.rus.ec',
    tests_requires=['pytest'],
    py_modules=['libgen'],
    entry_points={
        'console_scripts': ['libgen=libgen:main'],
    },
    install_requires=['beautifulsoup4', 'tabulate', 'requests']
)
