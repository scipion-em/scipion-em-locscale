# ******************************************************************************
# *
# * Authors:     Grigory Sharov     (gsharov@mrc-lmb.cam.ac.uk)
# *
# * MRC Laboratory of Molecular Biology, MRC-LMB
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
# ******************************************************************************
import os.path

import pyworkflow.protocol.params as params
from pyworkflow.viewer import DESKTOP_TKINTER, ProtocolViewer
from pwem.viewers import ChimeraView, DataView

from .protocols import ProtLocScale
from .constants import VOLUME_CHIMERA, VOLUME_SLICES


class LocscaleViewer(ProtocolViewer):
    """ Visualization of LocScale locally sharpened maps. """

    _environments = [DESKTOP_TKINTER]
    _targets = [ProtLocScale]
    _label = 'viewer'

    def _defineParams(self, form):
        form.addSection(label='Visualization')
        form.addParam('displayType', params.EnumParam,
                      choices=['slices', 'chimera'],
                      default=VOLUME_CHIMERA,
                      display=params.EnumParam.DISPLAY_HLIST,
                      label='Display volume with',
                      help='*slices*: display volumes as 2D slices along z axis.\n'
                           '*chimera*: display volumes as surface with Chimera.')
        form.addParam('displayVol', params.LabelParam,
                      label='Show locally sharpened map')

        if self.protocol.useNNpredict:
            form.addParam('doShowChimera', params.LabelParam,
                          label="Visualize confidence-weighted map in Chimera",
                          default=True,
                          help="LocScale Feature-Enhanced Maps computes a voxel-wise "
                               "confidence level of the optimised map, which we call "
                               "the predicted Voxel-Wise Difference Test (pVDDT) score. "
                               "pVDDT scores provide an intuitive way for objective map "
                               "interpretation by highlighting regions that may require "
                               "caution because. these regions display density that "
                               "significantly deviates from the density in "
                               "amplitude-only modified maps. Note that these scores "
                               "do not necessarily mean that these regions should not "
                               "be interpreted, just that their confidence is low(er).")

    def _getVisualizeDict(self):
        return {
            'displayVol': self._showVolume,
            'doShowChimera': self._showChimera
        }

    def _showVolume(self, paramName=None):
        fn = self._getOutputVolume()
        if not os.path.exists(fn):
            return [self.errorMessage(f"{fn} does not exist!")]

        view = []

        if self.displayType == VOLUME_CHIMERA:
            view.append(ChimeraView(self._showVolumeChimera(fn=fn)))
        elif self.displayType == VOLUME_SLICES:
            view.append(DataView(fn))

        return view

    def _showVolumeChimera(self, fn, cmdFile="chimera_volume.cxc"):
        """ Create a chimera script to visualize a volume. """
        cmdFile = self.protocol._getExtraPath(cmdFile)
        with open(cmdFile, 'w+') as f:
            localVol = os.path.basename(fn)
            f.write("open %s\n" % localVol)

        return cmdFile

    def _showChimera(self, param=None):
        """ Create a chimera script to visualize a volume with pVDDT score. """
        view = []
        fnResVol = self._getpVDDTVolumeName()
        fnMap = self._getOutputVolume()

        if not os.path.exists(fnResVol):
            return [self.errorMessage(f"{fnResVol} does not exist!")]
        if not os.path.exists(fnMap):
            return [self.errorMessage(f"{fnMap} does not exist!")]
        else:
            cmdFile = self._showVolumeChimera(fnMap, "chimera_pVDDT_score.cxc")
            with open(cmdFile, 'a') as f:
                localVol = os.path.basename(fnResVol)
                f.write("open %s\nvol #2 hide\n" % localVol)
                f.write("color sample #1 map #2 palette -95,#0000ff:"
                        "-80,#00ffff:0,#00ff00:80,#ffff00:95,#ff0000\n")
                view.append(ChimeraView(cmdFile))

        return view

    def _getOutputVolume(self):
        return self.protocol.getOutputFn("extra")

    def _getpVDDTVolumeName(self):
        return self.protocol._getExtraPath("pVDDT.mrc")
