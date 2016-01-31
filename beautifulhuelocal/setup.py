from distutils.core import setup
from beautifulhue import __version__

setup(
    name='BeautifulHue',
    version=__version__,
    author='Allan Bunch',
    packages=['beautifulhuelocal', 'beautifulhuelocal.api', 'beautifulhuelocal.libs'],
    url='https://github.com/allanbunch/beautifulhuelocal',
    license='MIT',
    description='A Python module for the Philips Hue Lighting System API.',
    long_description=open('README.md').read(),
    platforms="Cross Platform",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Topic :: Software Development',
        ],
)
