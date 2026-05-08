# **************************************************************************
# *
# * Authors: Yunior C. Fonseca Reyna    (cfonseca@cnb.csic.es) [1]
# *          Jiahua He                  (d201880053@hust.edu.cn) [2]
# *
# * [1] Unidad de  Bioinformatica of Centro Nacional de Biotecnologia , CSIC
# * [2] Sheng-You Huang and Huazhong University of Science and Technology
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

from pyworkflow.constants import BETA
import pyworkflow.protocol.params as params
from pyworkflow.utils import replaceBaseExt, getExt, createAbsLink
from pwem.convert.headers import setMRCSamplingRate
from pwem.objects import Volume
from pwem.protocols import ProtAnalysis3D
from pwem.emlib.image import ImageHandler

from .. import Plugin


class ProtEMReadySharpening(ProtAnalysis3D):
    """
    Sharpens a cryo-EM density map using the EMReady deep-learning framework.

    AI Generated:

    EMReady Sharpening (ProtEMReadySharpening) — User Manual
        Overview

        The EMReady Sharpening protocol performs local sharpening of cryo-EM density maps
        using the EMReady deep-learning framework. Its main purpose is to enhance local
        structural detail and improve the interpretability of reconstructed maps.

        For biological users, this protocol is typically applied after 3D reconstruction,
        when the map is already available but local regions remain blurred, weak, or
        difficult to interpret for downstream model building or structural analysis.

        Inputs and General Workflow

        The protocol requires one main input:

        - An input cryo-EM volume.

        Optionally, the protocol can also use:

        - A binary mask volume.
        - A structure mask in PDB or CIF format.

        During execution, the input map is converted to MRC format if necessary.
        If a mask is provided, it is also converted to MRC format and prepared
        for the sharpening run.

        The EMReady prediction program then processes the map using a sliding-window
        strategy, producing a sharpened output volume.

        Processing Workflow

        The protocol performs the following steps:

        - Converts or links the input map into MRC format.
        - Converts or links the optional mask into MRC format.
        - Reads the optional structural mask (PDB or CIF).
        - Launches the EMReady prediction program.
        - Produces a sharpened output map named `outputVol.mrc`.

        This wrapper therefore integrates EMReady sharpening directly into the Scipion
        workflow while preserving compatibility with downstream cryo-EM analysis.

        Sharpening Strategy

        EMReady uses overlapping 3D boxes extracted from the input volume.

        Two parameters control this process:

        Batch size:
            Defines how many boxes are processed simultaneously.
            Larger values improve speed but require more GPU memory.

        Stride:
            Defines the overlap between neighboring boxes.
            Smaller stride values produce denser local sampling and often
            smoother sharpening, but increase memory and runtime.

        The stride must remain within the range:

            12 ≤ stride ≤ 48

        From a biological perspective, smaller stride values are usually preferable
        when preserving fine local features is important.

        GPU and CPU Execution

        The protocol supports both GPU and CPU execution.

        By default, GPU execution is enabled because deep-learning inference
        is substantially faster on GPUs.

        Multiple GPUs may also be used by specifying several GPU IDs.

        If GPU execution is disabled, the protocol switches to CPU mode,
        which may be substantially slower for large cryo-EM maps.

        Optional Masks

        Two optional masking strategies can guide sharpening:

        Input mask:
            A volume mask defining the region of interest.

        Structure mask:
            A PDB or CIF file used as an additional structural prior.

        Biologically, masking can be particularly useful when sharpening
        complexes embedded in large solvent regions or when focusing on
        specific structural domains.

        Output Volume

        The protocol produces one output:

        - A locally sharpened volume.

        The output file is written as:

            outputVol.mrc

        The protocol also adjusts the output sampling rate:

        - If the input pixel size is greater than or equal to 1.0 Å,
          the output sampling rate is set to 1.0 Å.
        - If the input pixel size is smaller than 1.0 Å,
          the output sampling rate is set to 0.5 Å.

        This resampling behavior should be kept in mind when comparing the
        sharpened map to the original volume or when performing subsequent
        quantitative analyses.

        Biological Interpretation

        EMReady sharpening is particularly useful when the reconstructed map
        contains locally weak regions that obscure biologically meaningful
        structural features.

        Typical downstream applications include:

        - visual inspection of flexible regions,
        - improved backbone tracing,
        - improved side-chain visibility,
        - facilitating atomic model building.

        As with any learned enhancement method, the sharpened map should be
        interpreted together with the original map rather than as a direct
        replacement of the experimental density.

        Practical Recommendations

        In routine cryo-EM workflows, a useful strategy is:

        - start with the default stride,
        - use a moderate batch size adapted to available GPU memory,
        - provide a mask when solvent or non-target regions dominate the box.

        For very large maps, increasing batch size improves speed if GPU memory allows.
        For difficult local regions, decreasing stride usually improves local consistency.

        Final Perspective

        EMReady sharpening provides a practical deep-learning-based local enhancement
        strategy for cryo-EM maps.

        For most structural biology users, its main advantage is improved local
        interpretability while remaining fully integrated into standard Scipion
        reconstruction and model-building workflows.
    """
    _label = 'sharpening'
    _devStatus = BETA
    _OUTNAME = "sharpenedVolume"
    _possibleOutputs = {_OUTNAME: Volume}

    # --------------------------- DEFINE param functions ----------------------
    def _defineParams(self, form):
        form.addSection(label='Input')
        form.addHidden(params.USE_GPU, params.BooleanParam,
                       default=True,
                       label="Use GPU for execution",
                       help="This protocol has both CPU and GPU implementation. "
                            "Select the one you want to use.")
        form.addHidden(params.GPU_LIST, params.StringParam, default='0',
                       label="Choose GPU IDs",
                       help="GPU may have several cores. Set it to zero"
                            " if you do not know what we are talking about."
                            " First core index is 0, second 1 and so on."
                            " You can use multiple GPUs - in that case"
                            " set to i.e. *0 1 2*.")

        form.addParam('input_vol', params.PointerParam, pointerClass='Volume',
                      important=True,
                      label="Input volume",
                      help='Provide the input volume to be sharpened.')

        form.addParam('refMask', params.PointerParam, pointerClass='VolumeMask',
                      default=None,
                      label='Input mask',
                      allowsNull=True,
                      help='Input mask map in MRC2014 format (default: None)')

        form.addParam('refStructure', params.StringParam,
                      default=None,
                      label='Input mask in PDB or CIF format',
                      allowsNull=True,
                      help='Input structure mask files in PDB or CIF format (default: None)')

        form.addParam('batch_size', params.IntParam, default=10,
                      validators=[params.Positive],
                      label='Batch size',
                      help="Number of boxes input into EMReady in one batch. "
                           "Users can adjust batch_size according to the VRAM "
                           "of their GPU devices. Empirically, a GPU with "
                           "40 GB VRAM can afford a batch_size of 80.")

        form.addParam('stride', params.IntParam, default=12,
                      label='Stride for sliding window',
                      help="The step of the sliding window for cutting the "
                           "input map into overlapping boxes. Its value "
                           "should be an integer within [12,48]. The smaller, "
                           "the better, if your computer memory is enough.")

    # --------------------------- INSERT steps functions ----------------------
    def _insertAllSteps(self):
        self._insertFunctionStep(self.processStep, needsGPU=self.usesGpu())
        self._insertFunctionStep(self.createOutputStep, needsGPU=False)

    # --------------------------- STEPS functions -----------------------------
    def processStep(self):
        inputFn = self.input_vol.get().getFileName()
        mrcFn = os.path.join(self._getTmpPath(), replaceBaseExt(inputFn, 'mrc'))
        if getExt(inputFn) != ".mrc":
            ImageHandler().convert(inputFn, mrcFn)
            setMRCSamplingRate(mrcFn, self.input_vol.get().getSamplingRate())
        else:
            createAbsLink(os.path.abspath(inputFn), mrcFn)

        if self.refMask.get() is not None:
            inputMask = self.refMask.get().getFileName()
            maskFn = os.path.join(self._getTmpPath(), replaceBaseExt(inputMask, 'mrc'))
            if getExt(inputMask) != ".mrc":
                ImageHandler().convert(inputMask, maskFn)
                setMRCSamplingRate(maskFn, self.refMask.get().getSamplingRate())
            else:
                createAbsLink(os.path.abspath(inputMask), maskFn)
            maskFn = os.path.abspath(maskFn)
        else:
            maskFn = 'none'

        refStructure = self.refStructure.get()
        if refStructure is None:
            refStructure = 'none'

        args = [
            f"-i {os.path.abspath(mrcFn)}",
            f"-m {maskFn}",
            "-o outputVol.mrc",
            f"-p {str(refStructure)}",
            f"-b {self.batch_size}",
            f"-s {self.stride}",
            f"-md {self.getModelDir()}"
        ]

        if self.useGpu:
            args.append(f'-g {self.gpuList.get().replace(" ", ",")}')
        else:
            args.append("--use_cpu")

        program = Plugin.getHome("pred.py")
        self.runJob(Plugin.getProgram(program), " ".join(args),
                    env=Plugin.getEnviron(),
                    cwd=self._getExtraPath())

    def createOutputStep(self):
        """Return processed map"""
        out_vol = Volume()
        in_apix = self.input_vol.get().getSamplingRate()
        if in_apix >= 1.0:
            out_vol.setSamplingRate(1.0)
        else:
            out_vol.setSamplingRate(0.5)

        out_vol.setFileName(self._getExtraPath('outputVol.mrc'))

        self._defineOutputs(**{self._OUTNAME: out_vol})
        self._defineTransformRelation(self.input_vol, out_vol)

    # --------------------------- INFO functions ------------------------------
    def _validate(self):
        errors = []
        if not (12 <= self.stride <= 48):
            errors.append("Stride should be within [12, 48]")

        return errors

    def _summary(self):
        summary = []
        if not hasattr(self, self._OUTNAME):
            summary.append("Output volume not ready yet.")
        else:
            summary.append('We obtained a locally sharpened volume from the %s'
                           % self.getObjectTag('input_vol'))
        return summary

    # --------------------------- UTILS functions -----------------------------
    def getModelDir(self):
        return os.path.abspath(Plugin.getHome(f"model_state_dicts"))
