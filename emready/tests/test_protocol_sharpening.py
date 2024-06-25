# ***************************************************************************
# *
# * Authors:     Pablo Conesa (pconesa@cnb.csic.es) [1]
# *
# * [1] Unidad de  Bioinformatica of Centro Nacional de Biotecnologia , CSIC
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
# ***************************************************************************
import logging
logger = logging.getLogger(__name__)

from pyworkflow.utils import magentaStr
from pyworkflow.tests import BaseTest, setupTestProject, DataSet
from pwem.protocols import ProtImportVolumes

from ..protocols import ProtEMReadySharpening


class TestEMReadySharpening(BaseTest):
    @classmethod
    def setUpClass(cls):
        setupTestProject(cls)
        cls.dataSet = DataSet.getDataSet('xmipp_tutorial')

        logger.info(magentaStr("\n==> Importing data - volumes:"))
        pImpVolume = cls.newProtocol(ProtImportVolumes, samplingRate=9.9,
                                     filesPath=cls.dataSet.getFile('vol1'))

        cls.launchProtocol(pImpVolume, wait=True)
        cls.inputVol = pImpVolume.outputVolume

    def testSharpening(self):
        logger.info(magentaStr("\n==> Testing EMReady - sharpening:"))

        def launchTest(vol, expectedDimensions):
            emReadyProtocol = self.newProtocol(ProtEMReadySharpening,
                                               input_vol=vol,
                                               batch_size=20,
                                               stride=48)
            self.launchProtocol(emReadyProtocol)

            outputVol = getattr(emReadyProtocol, emReadyProtocol._OUTNAME)
            self.assertIsNotNone(outputVol)
            self.assertEqual(expectedDimensions, outputVol.getDim())
            self.assertEqual(1, outputVol.getSamplingRate())

        launchTest(vol=self.inputVol, expectedDimensions=(64, 64, 64))
