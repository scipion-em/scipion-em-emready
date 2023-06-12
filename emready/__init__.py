# **************************************************************************
# *
# * Authors: Yunior C. Fonseca Reyna    (cfonseca@cnb.csic.es)
# *
# * Unidad de  Bioinformatica of Centro Nacional de Biotecnologia , CSIC
# *
# * This program is free software; you can redistribute it and/or modify
# * it under the terms of the GNU General Public License as published by
# * the Free Software Foundation; either version 3 of the License, or
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

import os
import pwem
from pyworkflow.utils import Environ

from .constants import *

__version__ = '3.0'
_references = ['He2023']


class Plugin(pwem.Plugin):
    _homeVar = EMREADY_HOME
    _pathVars = [EMREADY_HOME]
    _supportedVersions = [V1_0]
    _url = "https://github.com/scipion-em/scipion-em-emready"

    @classmethod
    def _defineVariables(cls):
        cls._defineEmVar(EMREADY_HOME, f"emready-{DEFAULT_EMREADY_VERSION}")
        cls._defineVar(EMREADY_ENV_ACTIVATION, DEFAULT_ACTIVATION_CMD)

    @classmethod
    def getEnviron(cls):
        """ Setup the environment variables needed to launch EMReady. """
        environ = Environ(os.environ)

        environ.update({
            'PATH': Plugin.getHome()
        }, position=Environ.BEGIN)

        return environ

    @classmethod
    def getEMReadyEnvActivation(cls):
        return cls.getVar(EMREADY_ENV_ACTIVATION)

    @classmethod
    def getDependencies(cls):
        condaActivationCmd = cls.getCondaActivationCmd()
        neededProgs = ['wget']
        if not condaActivationCmd:
            neededProgs.append('conda')

        return neededProgs

    @classmethod
    def defineBinaries(cls, env):
        for ver in VERSIONS:
            cls.addEMReadyPackage(env, ver,
                                  default=ver == DEFAULT_EMREADY_VERSION)

    @classmethod
    def addEMReadyPackage(cls, env, version, default=False):
        folder = f"emready-{version}"
        ENV_NAME = getEnvName(version)
        installCmds = [
            (f'cd .. && rmdir {folder} && '
             f'wget -c http://huanglab.phys.hust.edu.cn/EMReady/EMReady_v{version}.tgz && '
             f'tar -xf EMReady_v{version}.tgz && mv EMReady {folder}',
             ['environment.yml']),

            (f'{cls.getCondaActivationCmd()}'
             f'conda env create -n {ENV_NAME} -f environment.yml && '
             f'{cls.getEMReadyEnvActivation()} && conda install -y -c conda-forge gfortran && '
             f'f2py -c interp3d.f90 -m interp3d',
             ['interp3d.cpython-38-x86_64-linux-gnu.so']),
        ]

        env.addPackage('emready', version=version,
                       commands=installCmds,
                       neededProgs=cls.getDependencies(),
                       tar="void.tgz",
                       default=default)

    @classmethod
    def getProgram(cls, program):
        """ Returns command line for an EMReady program. """
        return f'{cls.getCondaActivationCmd()} {cls.getEMReadyEnvActivation()} && python {program}'
