# Copyright 2019 Univa Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from setuptools import find_packages, setup

setup(
    name='unisight-data-bridge',
    use_scm_version={
        "root": "../..",
        "relative_to": __file__,
    },
    setup_requires=['setuptools_scm'],
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    python_requires='>=3.6',
    install_requires=[
      'werkzeug==0.16.1',
      'graphqlclient==0.2.4',
      'gunicorn==19.9.0',
      'numpy==1.17.4',
      'Flask==1.0.2',
      'pandas==1.0.5',
      'prometheus-client==0.6.0',
    ],
)
