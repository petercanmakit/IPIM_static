from setuptools import setup

setup(
    name='IPIM',
    packages=['IPIM'],
    include_package_data=True,
    install_requires=[
        'Flask>=0.2',
        'SQLAlchemy>=0.6'
    ],
)
