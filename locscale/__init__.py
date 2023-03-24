# **************************************************************************
# *
# * Authors:     David Maluenda (dmaluenda@cnb.csic.es)
# *              Yunior C. Fonseca Reyna (cfonseca@cnb.csic.es)
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

import pwem
import pyworkflow.utils as pwutils
from pyworkflow import Config

from .constants import *

__version__ = '3.1'
_logo = "locscale_logo.jpg"
_references = ['Jakobi2017', 'Bharadwaj2022']


class Plugin(pwem.Plugin):
    _supportedVersions = [V2_1]
    _url = "https://github.com/scipion-em/scipion-em-locscale"

    @classmethod
    def _defineVariables(cls):
        cls._defineVar(LOCSCALE_ENV_ACTIVATION, DEFAULT_ACTIVATION_CMD)

    @classmethod
    def getEnviron(cls, useCcp4=False):
        """ Setup the environment variables needed to launch LocScale. """
        if useCcp4:
            environ = cls.getCcp4Plugin().getEnviron()
            environ.update({'PATH': cls.getCcp4Plugin().getHome("bin")},
                           position=pwutils.Environ.BEGIN)
        else:
            environ = pwutils.Environ(os.environ)

        for v in ['PYTHONPATH', 'PYTHONHOME']:
            if v in environ:
                del environ[v]

        return environ

    @classmethod
    def getCcp4Plugin(cls):
        try:
            ccp4Plugin = pwem.Domain.importFromPlugin("ccp4", "Plugin",
                                                      doRaise=False)
            ccp4Plugin._defineVariables()
        except:
            return False

        return ccp4Plugin

    @classmethod
    def getDependencies(cls):
        """ Return a list of dependencies. Include conda if
        activation command was not found. """
        condaActivationCmd = cls.getCondaActivationCmd()
        neededProgs = []
        if not condaActivationCmd:
            neededProgs.append('conda')

        return neededProgs

    @classmethod
    def getActiveVersion(cls, *args):
        """ Return the env name that is currently active. """
        envVar = cls.getVar(LOCSCALE_ENV_ACTIVATION)
        return envVar.split()[-1].split("-")[-1]

    @classmethod
    def getLocscaleEnvActivation(cls):
        """ Remove the scipion home and activate the conda environment. """
        activation = cls.getVar(LOCSCALE_ENV_ACTIVATION)
        scipionHome = Config.SCIPION_HOME + os.path.sep

        return activation.replace(scipionHome, "", 1)

    @classmethod
    def getActivationCmd(cls):
        """ Return the activation command. """
        return '%s %s' % (cls.getCondaActivationCmd(),
                          cls.getLocscaleEnvActivation())

    @classmethod
    def getProgram(cls, program="run_locscale"):
        """ Create LocScale command line. """
        return f"{cls.getActivationCmd()} && locscale {program} "

    @classmethod
    def defineBinaries(cls, env):
        for ver in VERSIONS:
            cls.addLocscalePackage(env, ver,
                                   default=ver == LOCSCALE_DEFAULT_VER_NUM)

    @classmethod
    def addLocscalePackage(cls, env, version, default=False):
        ENV_NAME = f"locscale-{version}"
        FLAG = f"locscale_{version}_installed"

        # try to get CONDA activation command
        installCmds = [
            'touch refmac5 && chmod a+x refmac5 &&',  # fake binary for installer to work
            cls.getCondaActivationCmd(),
            f'conda create -y -n {ENV_NAME} python=3.8 gfortran -c conda-forge &&',
            f'conda activate {ENV_NAME} && pip install scikit-learn locscale &&',
            'rm -f refmac5 &&',
            f'touch {FLAG}'  # Flag installation finished
        ]
        finalCmds = [(" ".join(installCmds), FLAG)]

        envPath = os.environ.get('PATH', "")
        # locscale setup.py needs conda and refmac5 file in PATH
        installEnvVars = {'SKLEARN_ALLOW_DEPRECATED_SKLEARN_PACKAGE_INSTALL': 'True',
                          'PATH': f"{os.getcwd()}/{ENV_NAME}:{envPath}"}
        env.addPackage('locscale', version=version,
                       tar='void.tgz',
                       commands=finalCmds,
                       neededProgs=cls.getDependencies(),
                       default=default,
                       vars=installEnvVars)
