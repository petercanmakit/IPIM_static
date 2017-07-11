from setuptools import setup

setup(
    name='IPIM',
    packages=['IPIM'],
    include_package_data=True,
    install_requires=[
        'click>=6.7',
        'Flask>=0.12.1',
        'Flask-Session>=0.3.1',
        'Jinja2>=2.9.6',
        'psycopg2>=2.7.1',
        'radar>=0.3',
        'SQLAlchemy>=1.1.4',
        'Werkzeug>=0.12.1'
    ],
)
