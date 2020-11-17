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

import os

import pwem
import pyworkflow.utils as pwutils

from .constants import *

__version__ = '3.0.3'
_logo = "locscale_logo.jpg"
_references = ['Jakobi2017']


class Plugin(pwem.Plugin):
    _homeVar = LOCSCALE_HOME
    _pathVars = [LOCSCALE_HOME]
    _supportedVersions = [V0_1]

    @classmethod
    def _defineVariables(cls):
        cls._defineEmVar(LOCSCALE_HOME, 'locscale-0.1')

    @classmethod
    def getEnviron(cls):
        """ Setup the environment variables needed to launch resmap. """
        environ = pwutils.Environ(os.environ)
        environ.update({
            'PATH': Plugin.getHome(),
            'LD_LIBRARY_PATH': str.join(cls.getHome(), 'locscalelib')
                               + ":" + cls.getHome(),
        }, position=pwutils.Environ.BEGIN)

        return environ

    @classmethod
    def isVersionActive(cls):
        return cls.getActiveVersion().startswith(V0_1)

    @classmethod
    def getEmanPlugin(self):
        # --- Eman2 dependencies ---
        try:
            emanPlugin = Domain.importFromPlugin("eman2", "Plugin",
                                                 doRaise=True)
            emanPlugin._defineVariables()
        except Exception as e:
            print(pwutils.redStr("Eman plugin does not installed....You need to install it "
                  "first."))
            return None
        return emanPlugin

    @classmethod
    def getEmanDependencies(self):
        # to set the Eman2 environ in a bash-shell
        emanPlugin = self.getEmanPlugin()
        EMAN_ENV_STR = ' '.join(['%s=%s' % (var, emanPlugin.getEnviron()[var])
                                 for var in
                                 ('PATH', 'PYTHONPATH', 'LD_LIBRARY_PATH',
                                  'SCIPION_MPI_FLAGS')])
        return EMAN_ENV_STR

    @classmethod
    def defineBinaries(cls, env):
        emanPlugin = cls.getEmanPlugin()
        EMAN_ENV_STR = cls.getEmanDependencies()
        emanmpi4piFlag = "mpi4py-installed"
        env.addPackage('locscale', version='0.1',
                       tar='locscale-0.1.tgz',
                       commands=[('echo ; echo " > Installing mpi4py in eman2" && '
                                  'export %s && pip install mpi4py && touch %s' % (EMAN_ENV_STR, emanmpi4piFlag),
                                  emanPlugin.getHome('lib', 'python2.7', 'site-packages', 'mpi4py')),
                                 ('echo', 'source/locscale_mpi.py')],
                       default=True)
