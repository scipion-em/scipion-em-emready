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

__version__ = '2.0'


class Plugin(pwem.Plugin):

    _homeVar = EMREADY_HOME
    _pathVars = [EMREADY_HOME]
    _supportedVersions = [V1_3]
    _url = "https://github.com/scipion-em/scipion-em-emready"
    _processingField = [MODELLING]

    # ----------------------------------------------------------------------
    @classmethod
    def _defineVariables(cls):

        cls._defineEmVar(
            EMREADY_HOME,
            f"emready-{DEFAULT_EMREADY_VERSION}",
            description='Path to the folder where EMReady is located',
            var_type=VarTypes.PATH
        )

        cls._defineVar(
            EMREADY_ENV_ACTIVATION,
            DEFAULT_ACTIVATION_CMD,
            description='EMReady environment activation command',
            var_type=VarTypes.STRING
        )

    # ----------------------------------------------------------------------
    @classmethod
    def getEnviron(cls):
        environ = Environ(os.environ)

        environ.update({
            'PATH': Plugin.getHome()
        }, position=Environ.BEGIN)

        return environ

    # ----------------------------------------------------------------------
    @classmethod
    def getEMReadyEnvActivation(cls):
        return cls.getVar(EMREADY_ENV_ACTIVATION)

    # ----------------------------------------------------------------------
    @classmethod
    def getDependencies(cls):
        condaActivationCmd = cls.getCondaActivationCmd()
        neededProgs = ['wget', 'git']

        if not condaActivationCmd:
            neededProgs.append('conda')

        return neededProgs

    # ----------------------------------------------------------------------
    @classmethod
    def defineBinaries(cls, env):
        for ver in VERSIONS:
            cls.addEMReadyPackage(
                env,
                ver,
                default=(ver == DEFAULT_EMREADY_VERSION)
            )

    # ----------------------------------------------------------------------
    @classmethod
    def addEMReadyPackage(cls, env, version="2.0", default=True):

        installer = InstallHelper(
            "emready",
            packageHome=cls.getVar(EMREADY_HOME),
            packageVersion=version
        )

        envName = f"emready-{version}"
        repoUrl = "https://github.com/huang-laboratory/EMReady2.git"

        conda = cls.getCondaActivationCmd()

        installer.addCommand(
            f"git clone {repoUrl}",
            "clone_emready2"
        ).addCommand(
            f"{conda} conda create -y -n {envName} python=3.10",
            "create_env"
        ).addCommand(
            f"{conda} conda activate {envName} && "
            f"pip install torch==2.4.1 torchvision==0.19.1 torchaudio==2.4.1 "
            f"--index-url https://download.pytorch.org/whl/cu118",
            "install_torch"
        ).addCommand(
            f"{conda} conda activate {envName} && "
            f"cd EMReady2 && pip install -r requirements.txt",
            "install_requirements"
        ).addCommand(
            f"{conda} conda activate {envName} && "
            f"cd EMReady2 && "
            f"wget https://github.com/Dao-AILab/causal-conv1d/releases/download/v1.4.0/causal_conv1d-1.4.0+cu118torch2.4cxx11abiFALSE-cp310-cp310-linux_x86_64.whl && "
            f"wget https://github.com/state-spaces/mamba/releases/download/v2.2.0/mamba_ssm-2.2.0+cu118torch2.4cxx11abiFALSE-cp310-cp310-linux_x86_64.whl && "
            f"pip install causal_conv1d-1.4.0+cu118torch2.4cxx11abiFALSE-cp310-cp310-linux_x86_64.whl && "
            f"pip install mamba_ssm-2.2.0+cu118torch2.4cxx11abiFALSE-cp310-cp310-linux_x86_64.whl",
            "install_mamba"
        ).addCommand(
            f"{conda} conda activate {envName} && "
            f"cd EMReady2 && pip install -e . --no-deps",
            "install_emready2"
        ).addCommand(
            f"{conda} conda activate {envName} && "
            f"cd EMReady2 && "
            f"mkdir -p model_weights && "
            f"wget http://huanglab.phys.hust.edu.cn/EMReady2/model_weights/model_0p6.pt -O model_weights/model_0p6.pt && "
            f"wget http://huanglab.phys.hust.edu.cn/EMReady2/model_weights/model_1p0.pt -O model_weights/model_1p0.pt",
            "download_weights"
        )

        installer.addPackage(
            env,
            dependencies=['git', 'wget', 'conda'],
            default=default
        )

    # ----------------------------------------------------------------------
    @classmethod
    def getProgram(cls, program):
        return f'{cls.getCondaActivationCmd()} {cls.getEMReadyEnvActivation()} && python {program}'