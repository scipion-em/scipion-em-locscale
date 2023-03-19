# ***************************************************************************
# *
# * Authors:     David Maluenda (dmaluenda@cnb.csic.es)
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

from pyworkflow.tests import BaseTest, setupTestProject, DataSet
from pwem.protocols import ProtImportVolumes, ProtImportPdb
from pyworkflow.utils import magentaStr

from ..protocols import ProtLocScale


class TestProtLocscale(BaseTest):
    @classmethod
    def runImportVolumes(cls, samplingRate, vol, half1, half2):
        """ Run Import volumes protocol. """
        cls.protImport = cls.newProtocol(ProtImportVolumes,
                                         filesPath=vol,
                                         samplingRate=samplingRate,
                                         setHalfMaps=True,
                                         half1map=half1,
                                         half2map=half2)
        cls.launchProtocol(cls.protImport)
        return cls.protImport

    @classmethod
    def setUpClass(cls):
        setupTestProject(cls)
        cls.ds = DataSet.getDataSet('model_building_tutorial')
        cls.half1 = cls.ds.getFile('volumes/emd_3488_Noisy_half1.vol')
        cls.half2 = cls.ds.getFile('volumes/emd_3488_Noisy_half2.vol')
        cls.map = cls.ds.getFile('volumes/emd_3488.map')
        cls.model = cls.ds.getFile('PDBx_mmCIF/5ni1.pdb')

        print(magentaStr("\n==> Importing data - volume:"))
        cls.protImportMap = cls.runImportVolumes(1.05,
                                                 cls.map,
                                                 cls.half1,
                                                 cls.half2)

        print(magentaStr("\n==> Importing data - pdb:"))
        cls.protImportModel = cls.newProtocol(ProtImportPdb,
                                              inputPdbData=1,
                                              pdbFile=cls.model)
        cls.launchProtocol(cls.protImportModel)

    def testLocscale(self):
        print(magentaStr("\n==> Testing locscale:"))

        def launchTest(label, vol, volRef=None, pdbRef=None, useNN=False):
            print(magentaStr("\nTest %s:" % label))
            pLocScale = self.proj.newProtocol(ProtLocScale,
                                              objLabel='locscale - ' + label,
                                              inputVolume=vol)
            if useNN:
                pLocScale.useNNpredict.set(True)
            else:
                if volRef is not None:
                    pLocScale.refType.set(2)
                    pLocScale.refObj.set(volRef)
                elif pdbRef is not None:
                    pLocScale.refType.set(1)
                    pLocScale.refObj.set(pdbRef)
                else:
                    pLocScale.refType.set(0)

            self.proj.launchProtocol(pLocScale, wait=True)

            self.assertIsNotNone(pLocScale.outputVolume,
                                 "outputVolume is None for %s test." % label)

            self.assertEqual(self.inputVol.getDim(),
                             pLocScale.outputVolume.getDim(),
                             "outputVolume has a different size than inputVol "
                             "for %s test" % label)

            self.assertEqual(self.inputVol.getSamplingRate(),
                             pLocScale.outputVolume.getSamplingRate(),
                             "outputVolume has a different sampling rate than "
                             "inputVol for %s test" % label)

        inputVol = self.protImportMap.outputVolume
        pdbRef = self.protImportModel.outputPdb
        volRef = None

        launchTest('noRef', vol=inputVol)
        launchTest('volRef', vol=inputVol, volRef=volRef)
        launchTest('pdbRef', vol=inputVol, pdbRef=pdbRef)
        launchTest('EMmerNet', vol=inputVol, useNN=True)
