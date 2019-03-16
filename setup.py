from setuptools import setup
install_deps=['beautifulsoup4', 'BeautifulTable', 'requests']
test_deps = [
    'vcrpy',
    'pytest',
]
extras = {
    'test': test_deps,
}

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
    packages=['libgen'],
    include_package_data=True,  # include files listed in MANIFEST.in
    tests_require=test_deps,
    py_modules=['libgen'],
    python_requires='~=3.5',
    entry_points={
        'console_scripts': ['libgen=libgen.__main__:main'],
    },
    install_requires=install_deps,
    extras_require=extras,
)
