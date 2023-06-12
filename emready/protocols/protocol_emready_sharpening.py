# **************************************************************************
# *
# * Authors: Yunior C. Fonseca Reyna    (cfonseca@cnb.csic.es) [1]
# *          Jiahua He                  (d201880053@hust.edu.cn) [2]
# *
# * [1] Unidad de  Bioinformatica of Centro Nacional de Biotecnologia , CSIC
# * [2] Sheng-You Huang and Huazhong University of Science and Technology
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

from pyworkflow.constants import BETA
import pyworkflow.protocol.params as params
from pyworkflow.utils import replaceBaseExt, getExt, createAbsLink
from pwem.convert.headers import setMRCSamplingRate
from pwem.objects import Volume
from pwem.protocols import ProtAnalysis3D
from pwem.emlib.image import ImageHandler

from .. import Plugin


class ProtEMReadySharpening(ProtAnalysis3D):
    """ Wrapper protocol for EMReady to calculate the sharpened map. """
    _label = 'sharpening'
    _devStatus = BETA
    _OUTNAME = "sharpenedVolume"
    _possibleOutputs = {_OUTNAME: Volume}

    # --------------------------- DEFINE param functions ----------------------
    def _defineParams(self, form):
        form.addSection(label='Input')
        form.addHidden(params.USE_GPU, params.BooleanParam,
                       default=True,
                       label="Use GPU for execution",
                       help="This protocol has both CPU and GPU implementation. "
                            "Select the one you want to use.")
        form.addHidden(params.GPU_LIST, params.StringParam, default='0',
                       label="Choose GPU IDs",
                       help="GPU may have several cores. Set it to zero"
                            " if you do not know what we are talking about."
                            " First core index is 0, second 1 and so on."
                            " You can use multiple GPUs - in that case"
                            " set to i.e. *0 1 2*.")

        form.addParam('input_vol', params.PointerParam, pointerClass='Volume',
                      important=True,
                      label="Input volume",
                      help='Provide the input volume to be sharpened.')

        form.addParam('batch_size', params.IntParam, default=10,
                      label='Batch size',
                      help="Number of boxes input into EMReady in one batch. "
                           "Users can adjust batch_size according to the VRAM "
                           "of their GPU devices. Empirically, a GPU with "
                           "40 GB VRAM can afford a batch_size of 80.")

        form.addParam('stride', params.IntParam, default=12,
                      label='Stride for sliding window',
                      help="The step of the sliding window for cutting the "
                           "input map into overlapping boxes. Its value "
                           "should be an integer within [10,40]. The smaller, "
                           "the better, if your computer memory is enough.")

    # --------------------------- INSERT steps functions ----------------------
    def _insertAllSteps(self):
        self._insertFunctionStep(self.processStep)
        self._insertFunctionStep(self.createOutputStep)

    # --------------------------- STEPS functions -----------------------------
    def processStep(self):
        inputFn = self.input_vol.get().getFileName()
        mrcFn = os.path.join(self._getTmpPath(), replaceBaseExt(inputFn, 'mrc'))

        if getExt(inputFn) != ".mrc":
            ImageHandler().convert(inputFn, mrcFn)
            setMRCSamplingRate(mrcFn, self.input_vol.get().getSamplingRate())
        else:
            createAbsLink(os.path.abspath(inputFn), mrcFn)

        args = [
            f"-i {os.path.abspath(mrcFn)}",
            "-o outputVol.mrc",
            f"-b {self.batch_size}",
            f"-s {self.stride}",
            f"-m {self.getModelDir()}"
        ]

        if self.useGpu:
            args.append(f'-g {self.gpuList.get().replace(" ", ",")}')
        else:
            args.append("--use_cpu")

        program = Plugin.getHome("pred.py")
        self.runJob(Plugin.getProgram(program), " ".join(args),
                    env=Plugin.getEnviron(),
                    cwd=self._getExtraPath())

    def createOutputStep(self):
        """Return processed map"""
        out_vol = Volume()
        in_apix = self.input_vol.get().getSamplingRate()
        if in_apix >= 1.0:
            out_vol.setSamplingRate(1.0)
        else:
            out_vol.setSamplingRate(0.5)

        out_vol.setFileName(self._getExtraPath('outputVol.mrc'))

        self._defineOutputs(**{self._OUTNAME: out_vol})
        self._defineTransformRelation(self.input_vol, out_vol)

    # --------------------------- INFO functions ------------------------------
    def _validate(self):
        errors = []
        if not (12 <= self.stride <= 48):
            errors.append("Stride should be within [12, 48]")
        if self.batch_size <= 0:
            errors.append("Batch size should be greater than 0")

        return errors

    def _summary(self):
        summary = []
        if not hasattr(self, self._OUTNAME):
            summary.append("Output volume not ready yet.")
        else:
            summary.append('We obtained a locally sharpened volume from the %s'
                           % self.getObjectTag('input_vol'))
        return summary

    # --------------------------- UTILS functions -----------------------------
    def getModelDir(self):
        return os.path.abspath(Plugin.getHome(f"model_state_dicts"))
