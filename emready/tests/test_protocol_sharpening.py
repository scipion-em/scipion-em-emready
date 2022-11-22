# ***************************************************************************
# *
# * Authors:     Pablo COnesa (pconesa@cnb.csic.es) (2018)
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
# ***************************************************************************
import logging

from ..protocols.protocol_emready_sharpening import EMReadyOutputs

logger = logging.getLogger(__name__)
from pyworkflow.tests import BaseTest, setupTestProject, DataSet
from pwem.protocols import ProtImportVolumes, ProtImportMask
from pyworkflow.utils import magentaStr

from ..protocols import ProtEMReadySharppening


class TestEMReadySharpening(BaseTest):
    @classmethod
    def setUpClass(cls):
        setupTestProject(cls)
        cls.dataSet = DataSet.getDataSet('xmipp_tutorial')

        # Imports
        logger.info(magentaStr("\n==> Importing data - Input data"))
        new = cls.proj.newProtocol  # short notation
        launch = cls.proj.launchProtocol

        # Volumes
        logger.info(magentaStr("\nImporting Volumes:"))

        # Volume 1
        pImpVolume = new(ProtImportVolumes, samplingRate=9.9,
                         filesPath=cls.dataSet.getFile('vol2'))
        launch(pImpVolume, wait=True)
        cls.inputVol = pImpVolume.outputVolume

        # Volume 2
        pImpVolume2 = new(ProtImportVolumes, samplingRate=9.9,
                          filesPath=cls.dataSet.getFile('vol1'))

        launch(pImpVolume2, wait=True)
        cls.inputVol2 = pImpVolume2.outputVolume

        # This can be removed if not used
        # References
        # logger.info(magentaStr("\nImporting References:"))
        # pImpRef = new(ProtImportVolumes, samplingRate=1,
        #               filesPath=cls.dataSet.getFile('vol3'))
        # launch(pImpRef, wait=True)
        # #   reference.vol
        # cls.inputRef = pImpRef.outputVolume
        # pImpRef2 = new(ProtImportVolumes, samplingRate=1,
        #                filesPath=cls.dataSet.getFile('vol1'))
        # launch(pImpRef2, wait=True)
        # cls.inputRef2 = pImpRef2.outputVolume
        #
        # # Masks
        # logger.info(magentaStr("\nImporting Mask:"))
        # pImpMask = new(ProtImportMask,
        #                maskPath=cls.dataSet.getFile('mask3d'),
        #                samplingRate=1)
        # launch(pImpMask, wait=True)
        # cls.mask = pImpMask.outputMask

    def testSharpening(self):
        """ Check that an output was generated and the condition is valid.
            In addition, returns the size of the set.
        """
        logger.info(magentaStr("\n==> Testing EM ready:"))

        def launchTest(label, vol,expectedDimensions=(576, 576, 576)):

            logger.info(magentaStr("\nTest %s:" % label))
            emReadyProtocol = self.proj.newProtocol(ProtEMReadySharppening,
                                              objLabel='EMReady %s' % label,
                                              in_vol=vol,
                                              batch_size=20,
                                              stride=48)

            self.launchProtocol(emReadyProtocol)

            outputVol = getattr(emReadyProtocol, EMReadyOutputs.sharpenedVolume.name)
            self.assertIsNotNone(outputVol,
                                 "Sharpened volume is None for %s test." % label)

            self.assertEqual(expectedDimensions,
                             outputVol.getDim(),
                             "sharpened Volume has different size than inputVol "
                             "for %s test" % label)

            self.assertEqual(1,
                             outputVol.getSamplingRate(),
                             "sharpened Volume has different sampling rate than "
                             "inputVol for %s test" % label)

        # default test
        #launchTest('Vol 1', vol=self.inputVol)

        # vol 2
        launchTest('convert inputVol', vol=self.inputVol2, expectedDimensions=(576, 576, 576))
