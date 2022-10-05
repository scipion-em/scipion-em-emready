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
        """ Setup the environment variables needed to launch EMReady. """
        environ = Environ(os.environ)

        environ.update({
            'PATH': Plugin.getHome()
        }, position=Environ.BEGIN)

        return environ

    @classmethod
    def getEMReadyEnvActivation(cls):
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
    def defineBinaries(cls, env, pythonVersion='3.8'):
        EMReady_commands = []
        # Config conda env
        EMReady_commands.append(('conda create -y -n %s -c conda-forge -c pytorch ' \
                                 'python=%s pytorch==1.8.1 cudatoolkit=10.2 mrcfile numpy tqdm && touch emreadyEnv' \
                                 % (DEFAULT_ENV_NAME, pythonVersion), 'emreadyEnv'))
        EMReady_commands.append(("env_home=`conda info -e | awk '{if($1 == \"emreadyEnv\"){ if(NF == 2){print $2}else{print $3}}}'` && $env_home/bin/pip3 install einops timm", []))

        # Download sources codes from website
        EMReady_commands.append(('wget -c http://huanglab.phys.hust.edu.cn/EMReady/EMReady_v1.0.tgz', 'EMReady_v1.0.tgz'))
        EMReady_commands.append(('tar -xvf EMReady_v1.0.tgz', []))
        EMReady_commands.append(('cd EMReady && f2py -c interp3d.f90 -m interp3d', [])) 
        EMReady_commands.append(("cd EMReady && chmod u+rwx pred.py && env_home=`conda info -e | awk '{if($1 == \"emreadyEnv\"){ if(NF == 2){print $2}else{print $3}}}'` && sed -i \"1i #!$env_home/bin/python\" pred.py" , []))
        env.addPackage('EMReady', version=__version__,
                       commands=EMReady_commands,
                       tar=VOID_TGZ,
                       default=True)


    @classmethod
    def runEMReady(cls, protocol, program, args, cwd=None):
        """ Run EMReady command from a given protocol. """
        fullProgram = '%s' % (program)
        protocol.runJob(fullProgram, args, env=cls.getEnviron(), cwd=cwd,
                        numberOfMpi=1)


    @classmethod
    def getEMReadyModelStateDict10(cls):
        return os.path.abspath(cls.getVar(EMREADY_MODEL_STATE_DICT_10_VAR))

    @classmethod
    def getEMReadyModelStateDict05(cls):
        return os.path.abspath(cls.getVar(EMREADY_MODEL_STATE_DICT_05_VAR))

