import os
from setuptools import setup

version = {}
with open("pyilt2/version.py") as fp:
    exec(fp.read(), version)

# Utility function to read the README file.
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = 'pyilt2',
    version = version['__version__'],
    author = 'Frank Roemer',
    author_email = 'froemer76@googlemail.com',
    description = ("A library to access the ILThermo v2.0 database."),
    license = "MIT",
    keywords = "ILThermo, Ionic Liquids Database",
    url = "http://wgserve.de/pyilt2",
    packages=['pyilt2'],
    entry_points = {
        'console_scripts': ['pyilt2report=pyilt2.report:run'],
    },
    package_data={'': ['README', 'LICENSE', 'CHANGELOG','requirements.txt']},
    data_files = [('man/man1', ['pyilt2report.1'])],
    include_package_data=True,
    long_description=read('README'),
    install_requires=read('requirements.txt').splitlines(),
    classifiers=[
        'Operating System :: OS Independent',
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Education',
        'Intended Audience :: Developers',
        'Topic :: Database :: Front-Ends',
        'Topic :: Scientific/Engineering :: Chemistry',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3'
    ]
)
