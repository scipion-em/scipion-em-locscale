# **************************************************************************
# *
# * Authors:     David Maluenda (dmaluenda@cnb.csic.es)
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

from pyworkflow.utils import replaceBaseExt
from pwem.emlib.image import ImageHandler

from .constants import *
from . import Plugin


def getVersion():
    locscaleHome = Plugin.getVar(LOCSCALE_HOME)

    version = ''
    for v in getSupportedVersions():
        if v in locscaleHome:
            version = v
    return version


def getSupportedVersions():
    return ['0.1']


def getSupportedEmanVersions():
    """ LocScale needs eman to work.
    """
    return [V2_21, V2_3, V2_31]


def getEmanVersion():
    """ Returns a valid eman version installed or an empty string.
    """
    emanVersion = Plugin.getEmanPlugin().getHome()
    if os.path.exists(emanVersion):
        return emanVersion.split('-')[-1]
    return ''


def validateEmanVersion(errors):
    """ Validate if eman version is set properly according
     to installed version and the one set in the config file.
     Params:
        protocol: the input protocol calling to validate
        errors: a list that will be used to add the error message.
    """
    if getEmanVersion() not in getSupportedEmanVersions():
        errors.append('EMAN2 is needed to execute this protocol. '
                      'Install one of the following versions: %s.'
                      % ', '.join(getSupportedEmanVersions()))
    return errors


def getEmanPythonProgram(program):
    emanPlugin = Plugin.getEmanPlugin()
    env = emanPlugin.getEnviron()

    # locscale scripts are in $LOCSCALE_HOME/source
    program = Plugin.getHome('source', program)
    python = emanPlugin.getProgram('', True).split(' ')[0]

    return python, program, env


def convertBinaryVol(vol, outputDir):
    """ Convert binary volume to a mrc format.
    Params:
        vol: input volume object to be converted.
        outputDir: where to put the converted file(s)
    Return:
        new file name of the volume (converted or not).
    """
    ih = ImageHandler()

    def convertToMrc(fn):
        """ Convert from a format that is not read by Relion
        to mrc format.
        """
        newFn = os.path.join(outputDir, replaceBaseExt(fn, 'mrc'))
        ih.convert(fn, newFn)
        return newFn

    volFn = ih.removeFileType(vol.getFileName())

    if not volFn.endswith('.mrc'):
        volFn = convertToMrc(volFn)

    return volFn
