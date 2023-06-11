# **************************************************************************
# *
# * Authors: Yunior C. Fonseca Reyna    (cfonseca@cnb.csic.es)
# *
# *
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

import os
import pwem
import shutil
import pyworkflow as pw
from pyworkflow.utils import Environ
from scipion.install.funcs import VOID_TGZ
from .constants import *

__version__ = '3.0.0'


class Plugin(pwem.Plugin):
    _homeVar = EMREADY_HOME
    _pathVars = [EMREADY_HOME]

    @classmethod
    def _defineVariables(cls):
        default_emreadyHome = 'EMReady-%s' % DEFAULT_EMREADY_VERSION
        cls._defineEmVar(EMREADY_HOME, default_emreadyHome)
        cls._defineVar(EMREADY_ENV_ACTIVATION, DEFAULT_ACTIVATION_CMD)
        cls._defineEmVar(EMREADY_MODEL_STATE_DICT_10_VAR,
                         os.path.join(default_emreadyHome, EMREADY_MODEL_STATE_DICT_10))
        cls._defineEmVar(EMREADY_MODEL_STATE_DICT_05_VAR,
                         os.path.join(default_emreadyHome, EMREADY_MODEL_STATE_DICT_05))

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
    def isVersionActive(cls):
        return cls.getActiveVersion().startswith(__version__)

    @classmethod
    def getDependencies(cls):
        # try to get CONDA activation command
        condaActivationCmd = cls.getCondaActivationCmd()
        neededProgs = ['wget']
        if not condaActivationCmd:
            neededProgs.append('conda')

        return neededProgs

    @classmethod
    def defineBinaries(cls, env):

        emReadyInstalled = "emready_installed.txt"
        pythonVersion = "3.8"
        EMReady_commands = []
        # Config conda env
        EMReady_commands.append(('%s conda create -y -n %s -c conda-forge -c pytorch ' \
                                 'python=%s "pillow<7.0.0" pytorch==1.8.1 cudatoolkit=10.2 mrcfile numpy tqdm einops timm && '
                                 'touch %s' \
                                 % (cls.getCondaActivationCmd(), DEFAULT_ENV_NAME, pythonVersion, emReadyInstalled), [emReadyInstalled]))

        # Download sources codes from website
        EMReady_commands.append(('wget -c http://huanglab.phys.hust.edu.cn/EMReady/EMReady_v1.0.tgz', 'EMReady_v1.0.tgz'))
        EMReady_commands.append(('tar -xvf EMReady_v1.0.tgz', []))
        EMReady_commands.append(('cd EMReady && %s %s && f2py -c interp3d.f90 -m interp3d' % (cls.getCondaActivationCmd(), DEFAULT_ACTIVATION_CMD), []))
        env.addPackage('EMReady', version=DEFAULT_EMREADY_VERSION,
                       commands=EMReady_commands,
                       tar=VOID_TGZ,
                       default=True)


    @classmethod
    def runEMReady(cls, protocol, program, args, cwd=None):
        """ Run EMReady command from a given protocol. """
        fullProgram = '%s %s && python %s' % (cls.getCondaActivationCmd(), cls.getEMReadyEnvActivation(), program)
        protocol.runJob(fullProgram, args, env=cls.getEnviron(), cwd=cwd,
                        numberOfMpi=1)


    @classmethod
    def getEMReadyModelStateDict10(cls):
        return os.path.abspath(cls.getVar(EMREADY_MODEL_STATE_DICT_10_VAR))

    @classmethod
    def getEMReadyModelStateDict05(cls):
        return os.path.abspath(cls.getVar(EMREADY_MODEL_STATE_DICT_05_VAR))

