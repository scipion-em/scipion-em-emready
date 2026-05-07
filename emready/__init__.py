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
from pyworkflow import VarTypes, MODELLING
from pyworkflow.utils import Environ
from scipion.install.funcs import InstallHelper

from .constants import *

__version__ = '3.1.2'


class Plugin(pwem.Plugin):
    _homeVar = EMREADY_HOME
    _pathVars = [EMREADY_HOME]
    _supportedVersions = [V1_3]
    _url = "https://github.com/scipion-em/scipion-em-emready"
    _processingField = [MODELLING]

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
    def addEMReadyPackage(cls, env, version="1.3", default=True):
        installer = InstallHelper(
            "emready",
            packageHome=cls.getVar(EMREADY_HOME),
            packageVersion=version
        )

        envName = f"emready-{version}"

        installer.addCommand(
            f"wget -c http://huanglab.phys.hust.edu.cn/EMReady/EMReady_v{version}.tgz",
            "download_emready"
        ).addCommand(
            f"tar -xf EMReady_v{version}.tgz",
            "extract_emready"
        )

        installer.addCommand(
            f"conda env create -f EMReady_v{version}/environment.yml -n {envName}",
            "create_env"
        ).addCommand(
            f"conda install -n {envName} -y -c conda-forge 'setuptools<60' gfortran",
            "fix_dependencies"
        ).addCommand(
            f"cd EMReady_v{version} && "
            f"conda run -n {envName} bash -c '[ -f interp3d.f90 ] && f2py -c interp3d.f90 -m interp3d || true'",
            "compile_interp3d"
        ).addCommand(
            f"touch EMReady_v{version}/emready_installed",
            "emready_installed"
        )

        installer.addPackage(
            env,
            dependencies=['conda', 'wget'],
            default=default
        )

    @classmethod
    def getProgram(cls, program):
        """ Returns command line for an EMReady program. """
        return f'{cls.getCondaActivationCmd()} {cls.getEMReadyEnvActivation()} && python {program}'
