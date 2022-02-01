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


from pwem.protocols import ProtAnalysis3D
from pyworkflow.protocol.params import PointerParam


class ProtEMReadySharppening(ProtAnalysis3D):
    """
    Wrapper protocol for the EMReady's to calculate the sharpened map.
    """
    _label = 'sharppening'

    def _defineParams(self, form):
        form.addSection(label='Input')
        form.addParam('refVolume', PointerParam, pointerClass='Volume',
                      important=True,
                      label="Input volume",
                      help='Provide a reference volume for sharpening')

        # -----------[Sharppening]------------------------
        form.addSection(label="Sharpening")


    def _insertAllSteps(self):
        self._insertFunctionStep(self.createConfigStep)
        self._insertFunctionStep(self.processStep)
        self._insertFunctionStep(self.createOutputStep)



    def createConfigStep(self):
        pass

    def processStep(self):
        pass


    def createOutputStep(self):
        pass

    def _validate(self):
        pass

    def _summary(self):
        summary = []
        return summary
