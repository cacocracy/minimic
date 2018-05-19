from setuptools import setup

setup(name='minimic',
      version='0.0',
      description='Tools for minimic',
      url=None,
      author='Cacocracy',
      author_email=None,
      license='Unlicense',
      packages=['minimic'],
      zip_safe=False,
      install_requires=[
        'mypy',
        'HTMLParser',
        'requests',
        'pyquery',
        'Werkzeug'
      ],
      scripts=['bin/minimic'])

