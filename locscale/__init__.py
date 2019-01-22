# **************************************************************************
# *
# * Authors:     David Maluenda (dmaluenda@cnb.csic.es)
# *              Yunior C. Fonseca Reyna (cfonseca@cnb.csic.es)
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
"""
This package contains the protocols and data for LocScale
"""

import os

import pyworkflow.em
from pyworkflow.utils import Environ

from bibtex import _bibtex  # Load bibtex dict with references
from locscale.constants import *


_logo = "locscale_logo.jpg"


class Plugin(pyworkflow.em.Plugin):
    _homeVar = LOCSCALE_HOME_VAR
    _pathVars = [LOCSCALE_HOME_VAR]
    _supportedVersions = [V0_1]

    @classmethod
    def _defineVariables(cls):
        cls._defineEmVar(LOCSCALE_HOME_VAR, 'locscale-0.1')
        cls._defineEmVar(LOCSCALE_EMAN_HOME_VAR, EMAN_HOME_DEFAULT)


    @classmethod
    def getEnviron(cls):
        """ Setup the environment variables needed to launch resmap. """
        environ = Environ(os.environ)
        environ.update({
            'PATH': Plugin.getHome(),
            'LD_LIBRARY_PATH': str.join(cls.getHome(), 'locscalelib')
                           + ":" + cls.getHome(),
        }, position=Environ.BEGIN)

        return environ

    @classmethod
    def isVersionActive(cls):
        return cls.getActiveVersion().startswith(V0_1)

    @classmethod
    def defineBinaries(cls, env):

        env.addPackage('locscale', version='0.1',
                       tar='locscale-0.1.tgz',
                       default=True)


pyworkflow.em.Domain.registerPlugin(__name__)
