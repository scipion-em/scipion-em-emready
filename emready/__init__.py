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
from pyworkflow import VarTypes
from pyworkflow.utils import Environ

from .constants import *

__version__ = '3.1.0'
_references = ['He2023']


class Plugin(pwem.Plugin):
    _homeVar = EMREADY_HOME
    _pathVars = [EMREADY_HOME]
    _supportedVersions = [V2_0]
    _url = "https://github.com/scipion-em/scipion-em-emready"

    @classmethod
    def _defineVariables(cls):
        cls._defineEmVar(EMREADY_HOME, f"emready-{DEFAULT_EMREADY_VERSION}",
                         description='Path to the folder where EMReady is located',
                         var_type=VarTypes.PATH)
        cls._defineVar(EMREADY_ENV_ACTIVATION, DEFAULT_ACTIVATION_CMD,
                       description='EMReady environment activation command',
                       var_type=VarTypes.STRING)

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
        from scipion.install.funcs import CondaCommandDef
        folder = f"emready-{version}"
        ENV_NAME = getEnvName(version)

        installCmd = CondaCommandDef(ENV_NAME, cls.getCondaActivationCmd())
        installCmd.append(f'cd .. && rm -rf {folder} && '
                          f'wget -c http://huanglab.phys.hust.edu.cn/EMReady/v2.0/EMReady_v{version}.tgz && '
                          f'tar -xf EMReady_v{version}.tgz && mv EMReady_v{version} {folder}',
                          targets='environment.yml')
        installCmd.new()
        installCmd.create(yml='environment.yml')
        installCmd.new(targets='interp3d.cpython-39-x86_64-linux-gnu.so')
        installCmd.condaInstall('-y -c conda-forge gfortran libxcrypt && export CPATH=$CONDA_PREFIX/include && f2py -c interp3d.f90 -m interp3d')

        env.addPackage('emready', version=version,
                       commands=installCmd.getCommands(),
                       neededProgs=cls.getDependencies(),
                       tar="void.tgz",
                       default=default)

    @classmethod
    def getProgram(cls, program):
        """ Returns command line for an EMReady program. """
        return f'{cls.getCondaActivationCmd()} {cls.getEMReadyEnvActivation()} && python {program}'
