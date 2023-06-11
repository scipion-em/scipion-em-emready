# **************************************************************************
# *
# * Authors: 
# *    Jiahua He (d201880053@hust.edu.cn)
# *    Tao Li (d202280084@hust.edu.cn)
# *    Yunior C. Fonseca Reyna    (cfonseca@cnb.csic.es)
# *    Sheng-You Huang (huangsy@hust.edu.cn)
# *
# * School of Physics, Huangzhong University of Science and Technology
# * Unidad de  Bioinformatica of Centro Nacional de Biotecnologia , CSIC
# *
# * This program is free software; you can redistribute it and/or modify
# * it under the terms of the GNU General Public License as published by
# * the Free Software Foundation; either version 2 of the License, or
# * (at your option) any later version.
# *
# * This program is distributed in the hope that it will be useful,
# * but WITHOUT ANY WARRANTY; without even the implied warranty of
# * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# * GNU General Public License for more details.
# *
# * You should have received a copy of the GNU General Public License
# * along with this program; if not, write to the Free Software
# * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA
# * 02111-1307  USA
# *
# *  All comments concerning this program package may be sent to the
# *  e-mail address 'scipion@cnb.csic.es'
# *
# **************************************************************************

"""A setuptools based setup module.
See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path
from emready  import __version__

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

# Load requirements.txt
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='scipion-em-emready',  # Required
    version=__version__,  # Required
    description='EMReady: Improvement of cryo-EM maps by simultaneous local and non-local deep learning',  # Required

    long_description=long_description,  # Optional

    url='https://github.com/scipion-em/scipion-em-emready',  # Optional

    author='Jiahua He, Tao Li, Yunior C. Fonseca Reyna, Sheng-You Huang',  # Optional

    author_email='d201880053@hust.edu.cn, d202280084@hust.edu.cn, cfonseca@cnb.csic.es, huangsy@hust.edu.cn',  # Optional

    classifiers=[  # Optional
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        #   'Intended Audience :: Users',

        # Pick your license as you wish
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3.8'
    ],

    keywords='scipion electron-microscopy cryo-em structural-biology image-processing scipion-3.0 emready',  # Optional

    packages=find_packages(),

    package_data={  # Optional
       'emready': ['protocols.conf'],
    },

    project_urls={  # Optional
        'Bug Reports': 'https://github.com/scipion-em/scipion-em-emready/issues',
        'Source': 'https://github.com/scipion-em/scipion-em-emready/',
    },
    install_requires=[requirements],
    entry_points={
        'pyworkflow.plugin': 'emready = emready'
    },
)
