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
import pyworkflow as pw
from pyworkflow.utils import Environ
from .constants import *
__version__ = '0.0.1'


class Plugin(pwem.Plugin):
    _homeVar = EMREADY_HOME
    _pathVars = [EMREADY_HOME]

    @classmethod
    def _defineVariables(cls):
        emreadyHome = 'EMReady-%s' % __version__
        cls._defineEmVar(EMREADY_HOME, emreadyHome)
        cls._defineVar(EMREADY_ENV_ACTIVATION, DEFAULT_ACTIVATION_CMD)
        cls._defineEmVar(EMREADY_MODEL_STATE_DICT_10_VAR,
                         os.path.join(emreadyHome, EMREADY_MODEL_STATE_DICT_10))
        cls._defineEmVar(EMREADY_MODEL_STATE_DICT_05_VAR,
                         os.path.join(emreadyHome, EMREADY_MODEL_STATE_DICT_05))

    @classmethod
    def getEnviron(cls):
        """ Setup the environment variables needed to launch EmReady. """
        environ = Environ(os.environ)

        environ.update({
            'PATH': Plugin.getHome()
        }, position=Environ.BEGIN)

        return environ

    @classmethod
    def getEmReadyEnvActivation(cls):
        activation = cls.getVar(EMREADY_ENV_ACTIVATION)
        scipionHome = pw.Config.SCIPION_HOME + os.path.sep

        return activation.replace(scipionHome, "", 1)

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
    def addEmReadyPackage(cls, env, version, default=False, pythonVersion='3.8'):

        installationCmd = cls.getCondaActivationCmd()
        # Creating the environment
        installationCmd += ' conda create -y -n %s -c conda-forge -c anaconda ' \
                           'python=%s pytorch>1.6 mrcfile numpy tqdm' \
                            % (DEFAULT_ENV_NAME, pythonVersion)

        emready_commands = [(installationCmd, [])]

        env.addPackage('EMReady',
                       version=version,
                       #url='http://huanglab.phys.hust.edu.cn/EMReady/EMReady.tar',
                       tar='EMReady.tgz',
                       commands=emready_commands,
                       neededProgs=cls.getDependencies(),
                       default=default)

    @classmethod
    def runEmReady(cls, protocol, program, args, cwd=None):
        """ Run EMReady command from a given protocol. """
        fullProgram = '%s %s && %s' % (cls.getCondaActivationCmd(),
                                       cls.getEmReadyEnvActivation(),
                                       program)
        protocol.runJob(fullProgram, args, env=cls.getEnviron(), cwd=cwd,
                        numberOfMpi=1)

    @classmethod
    def getEMReadyModelStateDict10(cls):
        return os.path.abspath(cls.getVar(EMREADY_MODEL_STATE_DICT_10_VAR))

    @classmethod
    def getEMReadyModelStateDict05(cls):
        return os.path.abspath(cls.getVar(EMREADY_MODEL_STATE_DICT_05_VAR))

    @classmethod
    def defineBinaries(cls, env):
        cls.addEmReadyPackage(env, __version__,
                              default=bool(cls.getCondaActivationCmd()))

