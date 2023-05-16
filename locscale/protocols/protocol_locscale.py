# **************************************************************************
# *
# * Authors:    David Maluenda (dmaluenda@cnb.csic.es)
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

from pwem.protocols import Prot3D
from pwem.objects import Volume
from pyworkflow.protocol import params
from pyworkflow.utils import removeBaseExt, createLink, moveFile

from ..convert import convertBinaryVol
from ..constants import REF_VOL, REF_PDB, REF_NONE
from .. import Plugin


class ProtLocScale(Prot3D):
    """ This protocol computes contrast-enhanced cryo-EM maps
        by local amplitude scaling, optionally using a reference model.
    """
    _label = 'local sharpening'

    # --------------------------- DEFINE param functions ----------------------
    def _defineParams(self, form):
        form.addSection(label='Input')
        form.addHidden(params.GPU_LIST, params.StringParam, default='0',
                       label="Choose GPU IDs",
                       help="GPU may have several cores. Set it to zero"
                            " if you do not know what we are talking about."
                            " First core index is 0, second 1 and so on."
                            " You can use multiple GPUs - in that case"
                            " set to i.e. *0 1 2*.")

        form.addParam('inputVolume', params.PointerParam,
                      pointerClass='Volume',
                      important=True, label='Input EM map',
                      help='Input EM map, should be unsharpened and unfiltered.')

        form.addParam('useNNpredict', params.BooleanParam,
                      default=False, label="Use EMmerNet predictions?",
                      help="LocScale also supports local sharpening based "
                           "on a physics-inspired deep neural network "
                           "prediction method using our ensemble network "
                           "EMmerNet.")

        form.addParam('emmernetModel', params.EnumParam, default=0,
                      condition='useNNpredict',
                      choices=['model_based', 'model_free', 'ensemble'],
                      label="EMmerNet model")

        form.addParam('symmetryGroup', params.StringParam, default='c1',
                      condition='not useNNpredict',
                      label="Symmetry",
                      help="If your map has point group symmetry, you need "
                           "to specify the symmetry to force the pseudomodel "
                           "generator for produce a symmetrised reference "
                           "map for scaling.")

        form.addParam('refType', params.EnumParam, default=REF_PDB,
                      condition='not useNNpredict',
                      choices=['None', 'PDB', 'Volume'],
                      display=params.EnumParam.DISPLAY_HLIST,
                      label='Reference type:')

        form.addParam('refPdb', params.PointerParam,
                      condition='refType==1 and not useNNpredict',
                      label="Reference PDB model",
                      pointerClass="AtomStruct", allowsNull=True,
                      help="PDBx/mmCIF file of the reference atomic model.")

        form.addParam('incompletePdb', params.BooleanParam,
                      default=False,
                      condition='refType==1 and not useNNpredict',
                      label="Is atomic model partial?",
                      help="Add pseudo-atoms to areas of the map "
                           "which are not modelled.")

        form.addParam('refObj', params.PointerParam,
                      condition='refType==2 and not useNNpredict',
                      label="Reference volume",
                      pointerClass='Volume', allowsNull=True,
                      help='Model map file take it as reference '
                           '(usually this volume should come from a PDB).')

        form.addSection(label='Extra')
        form.addParam('binaryMask', params.PointerParam,
                      condition='not useNNpredict',
                      pointerClass='VolumeMask',
                      label='3D mask (optional)', allowsNull=True,
                      help='Binary mask')

        form.addParam('resol', params.IntParam, default=3,
                      condition='not useNNpredict',
                      label="Target resolution (A)",
                      help="Resolution target for Refmac refinement.")

        form.addParam('extraParams', params.StringParam, default='',
                      expertLevel=params.LEVEL_ADVANCED,
                      label='Additional parameters',
                      help="Extra command line parameters. "
                           "See *locscale run_locscale --help*.")

        form.addParallelSection(threads=3, mpi=1)

    # --------------------------- INSERT steps functions ----------------------
    def _insertAllSteps(self):
        self._insertFunctionStep(self.convertStep)
        self._insertFunctionStep(self.refineStep)
        self._insertFunctionStep(self.createOutputStep)

    # --------------------------- STEPS functions -----------------------------
    def convertStep(self):
        tmpFn = self._getTmpPath()
        self.inputVolsFn = []
        vol = self.inputVolume.get()
        if vol.hasHalfMaps():
            for v in vol.getHalfMaps(asList=True):
                self.inputVolsFn.append(convertBinaryVol(v, tmpFn))
        else:
            self.inputVolsFn.append(convertBinaryVol(vol, tmpFn))

        if not self.useNNpredict:
            if self.refType == REF_PDB:
                pdbFn = self.refPdb.get().getFileName()
                self.refPdbFn = self._getTmpPath(os.path.basename(pdbFn))
                createLink(pdbFn, self.refPdbFn)
            elif self.refType == REF_VOL:
                self.refVolFn = convertBinaryVol(self.refObj.get(), tmpFn)

            if self.binaryMask.hasValue():
                self.maskVolFn = convertBinaryVol(self.binaryMask.get(), tmpFn)

    def refineStep(self):
        """ Run the LocScale program. """
        program = "run_emmernet" if self.useNNpredict else "run_locscale"
        args = self.prepareParams(program)
        if self.extraParams.hasValue():
            args += ' ' + self.extraParams.get()

        if self.numberOfMpi > 1:
            # insert "mpirun -np X" after conda activation cmd
            mpiCmd = self.hostConfig.mpiCommand.get() % {
                'JOB_NODES': self.numberOfMpi,
                'COMMAND': f"locscale {program}"}
            cmd = f"{Plugin.getActivationCmd()} && {mpiCmd}"
        else:
            cmd = Plugin.getProgram(program)

        env = Plugin.getEnviron(useCcp4=self.checkCcp4())
        self.runJob(cmd, args, cwd=self._getTmpPath(),
                    env=env, numberOfThreads=1, numberOfMpi=1)

        # Move the resulting volume
        if os.path.exists(self.getOutputFn("tmp")):
            moveFile(self.getOutputFn("tmp"), self.getOutputFn("extra"))

    def createOutputStep(self):
        """ Create the output volume. """
        outputVolume = Volume()
        outputVolume.setSamplingRate(self.getSampling())
        outputVolume.setFileName(self.getOutputFn("extra"))
        self._defineOutputs(outputVolume=outputVolume)
        self._defineTransformRelation(self.inputVolume, outputVolume)

    # --------------------------- INFO functions ------------------------------
    def _warnings(self):
        warnings = []

        if not self.useNNpredict and not self.checkCcp4():
            warnings.append("CCP4 plugin is not installed. "
                            "Refmac5 refinement will be skipped.")

        return warnings

    def _validate(self):
        """ We validate if inputs make sense. """
        errors = []

        if self.useNNpredict and not self.inputVolume.get().hasHalfMaps():
            errors.append("EMmerNet predictions require two halfmaps "
                          "associated with an input volume.")

        inputVol = self.inputVolume.get()
        inputSize = inputVol.getDim()
        reference = self.refObj.get()

        if reference is not None:
            refSize = reference.getDim()
            refSamp = reference.getSamplingRate()

            if inputSize != refSize or self.getSampling() != refSamp:
                errors.append('Input map and reference volume should have '
                              'the same size and sampling rate')

        if (self.binaryMask.hasValue() and
                self.binaryMask.get().getDim() != inputSize):
            errors.append('Input map and binary mask should be '
                          'of the same size')

        if self.refType == REF_NONE and not self.checkCcp4():
            errors.append("Reference type = None requires REFMAC5 refinement. "
                          "CCP4 plugin was not found.")

        return errors

    def _summary(self):
        summary = []
        if not hasattr(self, 'outputVolume'):
            summary.append("Output volume not ready yet.")
        else:
            summary.append('We obtained a locally sharpened volume from the %s'
                           % self.getObjectTag('inputVolume'))
        return summary

    # --------------------------- UTILS functions -----------------------------
    def prepareParams(self, program="run_locscale"):
        args = [f"--outfile {os.path.basename(self.getOutputFn('tmp'))}",
                "--verbose"]

        inputVols = ' '.join(self.inputVolsFn)
        if len(self.inputVolsFn) > 1:
            args.append(f"--halfmap_paths {inputVols}")
        else:
            args.append(f"--emmap_path {inputVols}")

        if program == "run_emmernet":
            args.append(f"-trained_model {self.getEnumText('emmernetModel')}")
            args.append(f"--gpu_ids {' '.join(str(i) for i in self.getGpuList())}")
        else:  # run_locscale
            args.extend([f"--apix {self.getSampling()}",
                         f"--ref_resolution {self.resol.get()}"])

            if self.refType == REF_VOL:
                args.append(f"--model_map {self.refVolFn}")
            elif self.refType == REF_PDB:
                args.append(f"--model_coordinates {os.path.basename(self.refPdbFn)}")
                if self.incompletePdb:
                    args.append("--complete_model")

            if self.binaryMask.hasValue():
                args.append(f"--mask {self.maskVolFn}")

            if self.symmetryGroup.get() != "c1":
                args.append(f"--symmetry {self.symmetryGroup.get().upper()}")

            if self.numberOfMpi > 1:
                args.append("--mpi")

            if self.numberOfThreads > 1:
                args.append(f"--number_processes {self.numberOfThreads.get()}")

            if not self.checkCcp4():
                args.append("--skip_refine")

        return " ".join(args)

    def getSampling(self):
        return self.inputVolume.get().getSamplingRate()

    def getOutputFn(self, folder):
        """ Returns the scaled output file name. """
        outputFnBase = removeBaseExt(self.inputVolume.get().getFileName())
        return self._getPath(folder, outputFnBase) + '_scaled.mrc'

    def checkCcp4(self):
        return Plugin.getCcp4Plugin()
