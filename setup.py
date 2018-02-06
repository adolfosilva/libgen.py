from setuptools import setup

setup(
    name='libgen.py',
    version='0.1.0',
    license='MIT',
    author='Adolfo Silva',
    author_email='code@adolfosilva.org',
    url='https://github.com/adolfosilva/libgen.py',
    description='A script to download books from gen.lib.rus.ec',
    classifiers=[
        'License :: OSI Approved :: MIT License',
    ],
    keywords='libgen',
    include_package_data=True,  # include files listed in MANIFEST.in
    tests_requires=['pytest'],
    py_modules=['libgen'],
    entry_points={
        'console_scripts': ['libgen=libgen:main'],
    },
    install_requires=['beautifulsoup4', 'tabulate', 'requests']
)
