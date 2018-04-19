import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.md')) as f:
    README = f.read()
with open(os.path.join(here, 'CHANGES.txt')) as f:
    CHANGES = f.read()

requires = [
    'cornice',
    'plaster_pastedeploy',
    'psycopg2-binary',
    'pyramid >= 1.9a',
    'pyramid_debugtoolbar',
    'pyramid_jinja2',
    'pyramid_retry',
    'pyramid_tm',
    'pytest',
    'pytest-cov',
    'requests',
    'SQLAlchemy',
    'transaction',
    'zope.sqlalchemy',
    'waitress',
]

tests_require = [
    'WebTest >= 1.3.1',  # py3 compat
    'pytest',
    'pytest-cov',
    'requests',
]

setup(
    name='neuralknight',
    version='0.1.0a2',
    description='A Chess-playing AI',
    long_description=README + '\n\n' + CHANGES,
    author='David Snowberger, Shannon Tully, and Adam Grandquist',
    author_email='david.snowberger@fartherout.org',
    url='https://www.github.com/dsnowb/neuralknight',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Games/Entertainment :: Board Games',
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
        'Natural Language :: English',
        'License :: Freely Distributable',
        'Framework :: Pyramid',
        'Environment :: Console',
    ],
    keywords='chess entertainment game ai',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    extras_require={
        'testing': tests_require,
    },
    python_requires='>=3.5',
    install_requires=requires,
    entry_points={
        'paste.app_factory': [
            'main = neuralknight:main',
        ],
        'console_scripts': [
            'initialize_neuralknight_db = neuralknight.scripts.initializedb:main',
            'neuralknight = neuralknight.scripts.cli:main',
        ],
    },
)
