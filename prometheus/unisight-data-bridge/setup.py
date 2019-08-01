from setuptools import find_packages, setup

setup(
    name='unisight-data-bridge',
    version='1.0.0',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
      'graphqlclient',
      'gunicorn',
      'numpy',
      'Flask',
      'pandas',
      'prometheus-client',
    ],
)
