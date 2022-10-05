# **************************************************************************
# *
# * Authors: Yunior C. Fonseca Reyna    (cfonseca@cnb.csic.es)
# *
# * Unidad de  Bioinformatica of Centro Nacional de Biotecnologia , CSIC
# *
# * Authors: Jiahua He                  (d201880053@hust.edu.cn)
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

from pwem.objects import Volume
import pyworkflow.protocol.params as params
from pwem.protocols import ProtAnalysis3D
from pwem.emlib.image import ImageHandler

import os
import re
import emready
from emready.constants import *

class ProtEMReadySharppening(ProtAnalysis3D):
    """
    Wrapper protocol for the EMReady's to calculate the sharpened map.
    """
    _label = 'sharppening'

    def _defineParams(self, form):
        form.addSection(label='Input')

        form.addParam('use_gpu', params.BooleanParam, default=True,
                        label="Use GPU(s)?",
                        help='Whether run EMReady on GPU(s).')
        form.addParam('gpu_id', params.StringParam, default='0',
                        label='Choose GPU ID(s)', 
                        help='IDs of GPU devices to run EMReady, e.g. "0" for GPU #0, and "2,3,6" for GPUs #2, #3, and #6.')
        form.addParam('batch_size', params.IntParam, default=20,
                        label='Batch size',
                        help='Number of boxes input into EMReady in one batch. Users can adjust batch_size according to the VRAM of their GPU devices. Empirically, a GPU with 40 GB VRAM can afford a batch_size of 80.')


        group = form.addGroup('Input')
        group.addParam('in_vol', params.PointerParam, pointerClass='Volume',
                      important=True,
                      label="Input volume",
                      help='Provide the input volume to be sharpened.')

        group = form.addGroup('Advanced params')
        group.addParam('stride', params.IntParam, default=12,
                        label='Stride for sliding window.',
                        help='The step of the sliding window for cutting the input map into overlapping boxes. Its value should be an integer within [10,40]. The smaller, the better, if your computer memory is enough.')



    def _insertAllSteps(self):
        self._insertFunctionStep(self.createConfigStep)
        self._insertFunctionStep(self.processStep)
        self._insertFunctionStep(self.createOutputStep)

    def createConfigStep(self):
        stride = self.stride
        if self.use_gpu:
            use_gpu = 'true'
        else:
            use_gpu = 'false'
        gpu_id = self.gpu_id
        batch_size = self.batch_size

    def processStep(self):
        loc_in_vol = os.path.abspath(self.in_vol.get().getFileName())

        # Commands to run EMReady prediction
        emready_src_home = emready.Plugin.getVar(EMREADY_HOME)
        program = "%s/EMReady/pred.py" % (emready_src_home)

        if self.use_gpu:
            args = " -i {} -o out.map -g {} -b {} -s {} -m {}".format(loc_in_vol, self.gpu_id, self.batch_size, self.stride, emready_src_home + "/EMReady/model_state_dicts")
        else:
            args = " -i {} -o out.map --use_cpu -b {} -s {} -m {}".format(loc_in_col, self.batch_size, self.stride, emready_src_home + "/EMReady/model_state_dicts")

        emready.Plugin.runEMReady(self, program, args, cwd=self._getExtraPath())


    def createOutputStep(self):
        '''Return processed map'''
        out_vol = Volume()
        in_apix = self.in_vol.get().getSamplingRate()
        if in_apix >= 1.0:
            out_vol.setSamplingRate(1.0)
        else:
            out_vol.setSamplingRate(0.5)

        out_vol.setFileName(self._getExtraPath('out.map'))

        self._defineOutputs(outputVolume=out_vol)
        self._defineTransformRelation(self.in_vol, out_vol)


    def _validate(self):
        errors = []
        if (40 < self.stride or self.stride < 10):
            errors.append('`stride` should be within [10, 40].')
        elif (self.batch_size <= 0):
            errors.append('`batch_size` should > 0.')
        return errors

    def _summary(self):
        summary = []
        summary.append("Input volume : %s" % os.path.abspath(self.in_vol.get().getFileName()))
        return summary

    def _methods(self):
        methods = []
        return methods
