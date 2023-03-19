# **************************************************************************
# *
# * Authors:     David Maluenda (dmaluenda@cnb.csic.es)
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

from pyworkflow.utils import replaceBaseExt, createAbsLink
from pwem.emlib.image import ImageHandler


def convertBinaryVol(vol, outputDir):
    """ Convert binary volume to mrc format.
    Params:
        vol: input volume object to be converted.
        outputDir: where to put the converted file(s)
    Return:
        new file name of the volume (converted or not).
    """

    ih = ImageHandler()
    fn = vol if isinstance(vol, str) else vol.getFileName()
    newFn = os.path.join(outputDir, replaceBaseExt(fn, 'mrc'))

    if not fn.endswith('.mrc'):
        ih.convert(fn, newFn)
    else:
        createAbsLink(os.path.abspath(fn), newFn)

    return newFn
