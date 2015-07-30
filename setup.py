try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='ybk',
    version='0.1.0',
    description='Youbika Aggregation',
    url='https://github.com/observerss/ybk',
    author='Jingchao Hu(observerss)',
    author_email='jingchaohu@gmail.com',
    packages=['ybk'],
    package_data={'': ['LICENSE']},
    license=open('LICENSE').read(),
    install_requires=[
        'requests>=2.5',
        'flask>=0.10',
        'flask-login',
        'flask-assets',
        'jsmin',
        'cssmin',
        'bcrypt',
        'pyexecjs',
        'pyyaml',
        'lxml',
        'cssselect',
        'pymongo>=3',
        'python-dateutil',
        'xpinyin',
        'yamo>=0.2.6',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
    ],
    entry_points={
        'console_scripts': [
            'ybk=ybk.cli:main',
        ],
    }
)
