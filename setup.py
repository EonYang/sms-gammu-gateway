from setuptools import setup

VERSION = '0.0.1'

with open('./requirements.txt', 'r') as f:
    install_requires = f.read()


setup(
    name='mail_me_my_sms',
    version=VERSION,
    description='mail_me_my_sms',
    author='Yang',
    author_email='yy2473@nyu.edu',
    url='https://yangyang.blog/',
    packages=['mail_me_my_sms'],
    install_requires=install_requires,
    extras_require={
        'dev': [
            'pre-commit',
            'flake8',
            'pytest',
            'autopep8',
            'bump2version',
            'pytest-timeout'
        ],
        'test': [
            'pre-commit',
            'pytest',
            'pytest-timeout'
        ]
    }
)
