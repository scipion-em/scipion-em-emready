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
    Enhances cryo-EM density maps by applying local sharpening to improve
    the visibility of structural features and facilitate biological
    interpretation of reconstructed volumes.

    AI Generated:

    EMReady Sharpening (ProtEMReadySharpening) — User Manual
        Overview

        The EMReady Sharpening protocol is designed to improve the local interpretability of cryo-EM
        density maps by enhancing high-resolution structural detail while preserving the overall
        integrity of the reconstruction. In practical cryo-EM analysis, reconstructed maps often
        contain regions of uneven local quality. Flexible domains, solvent-exposed surfaces, and
        poorly ordered areas may appear blurred even when the global reconstruction reaches good
        nominal resolution. Local sharpening addresses this limitation by selectively increasing
        the contrast of meaningful features in different parts of the map.

        For biological users, this protocol is especially useful when preparing a map for visual
        inspection, atomic model building, structural interpretation, or figure generation.
        Sharpening often makes helices, strands, loops, side-chain densities, and local boundaries
        easier to recognize. The goal is not merely aesthetic enhancement but improved structural
        readability in regions where biologically important details may otherwise remain difficult
        to identify.

        Inputs and Biological Context

        The protocol requires an input volume representing the cryo-EM reconstruction that will
        be enhanced. In most workflows, this map is the result of refinement or post-processing,
        and should already be correctly sampled and centered. The quality of the sharpening depends
        strongly on the biological quality of the input map. If the map contains severe artifacts,
        strong masking effects, or major reconstruction errors, sharpening will not recover missing
        information and may instead emphasize undesirable features.

        Optionally, a mask can be provided. From a biological perspective, this can be extremely
        useful because it restricts the sharpening process to the molecular region of interest.
        Excluding solvent noise often improves local stability and reduces the risk of enhancing
        irrelevant background fluctuations. This becomes particularly important for membrane proteins,
        flexible assemblies, or complexes embedded in large solvent regions.

        A structural reference in PDB or CIF format may also be supplied. This is especially relevant
        when prior atomic knowledge exists, for example when refining a known homologous structure,
        interpreting a partially solved assembly, or guiding enhancement in systems where the
        experimental density contains uneven local information. The structural reference should be
        biologically compatible with the map; otherwise, it may bias interpretation rather than
        improve it.

        Local Sharpening Strategy

        Unlike global sharpening approaches that apply a uniform treatment to the entire map, local
        sharpening recognizes that different regions of a cryo-EM reconstruction may have very
        different local resolution or local reliability. A rigid core may contain well-defined
        secondary structure, while flexible peripheral regions may remain weak or noisy. Treating
        all regions equally often leads either to over-sharpening of noisy areas or under-sharpening
        of the most informative ones.

        The local approach is therefore particularly valuable for heterogeneous biological systems.
        Multi-domain proteins, large ribonucleoprotein assemblies, membrane complexes, and
        conformationally dynamic particles frequently benefit from this type of adaptive enhancement.
        In these contexts, sharpening can help reveal biologically relevant conformational boundaries
        and local architectural organization that may otherwise remain difficult to interpret.

        Batch Size and Computational Considerations

        The protocol processes the map in batches, which primarily affects GPU memory usage.
        Biologically, batch size does not change the interpretation of the result, but it strongly
        influences practical execution. Larger batch sizes improve throughput when sufficient GPU
        memory is available, whereas smaller values are safer for more limited hardware.

        For most users, this parameter is best regarded as a computational control rather than a
        biological one. If memory limitations are encountered, reducing the batch size is usually
        the safest strategy. This is especially relevant when working with large box sizes or
        high-resolution maps.

        Sliding Window and Locality

        A particularly important concept in this protocol is the sliding window strategy used to
        analyze the map locally. The stride controls how densely neighboring local regions overlap.

        From a biological perspective, smaller stride values generally provide smoother local
        adaptation and more consistent enhancement across structurally heterogeneous regions. This
        can be beneficial when studying flexible loops, domain interfaces, or subtle conformational
        transitions. However, smaller stride values also require more memory and longer runtime.

        Larger stride values reduce computational cost but may produce coarser local adaptation.
        For exploratory work, moderate default values are usually appropriate. For detailed
        interpretation of difficult maps, denser local sampling may yield better results.

        Outputs and Interpretation

        The protocol produces a sharpened volume that remains directly linked to the original map
        and can be used in downstream structural analysis. The output is intended to preserve the
        biological identity of the reconstruction while improving local contrast and readability.

        The sharpened map is especially useful during atomic model fitting, manual inspection of
        ambiguous regions, or visual comparison between different structural states. Users should
        nevertheless interpret the sharpened density carefully. Sharpening improves visibility of
        existing information but does not create new structural evidence. Features that appear
        sharper should still be evaluated against the underlying signal quality.

        Practical Recommendations

        In routine cryo-EM work, it is often advisable to begin with the default parameters and
        inspect whether secondary-structure features become more interpretable without obvious
        amplification of noise. When solvent noise is substantial, providing a suitable molecular
        mask often produces the most biologically meaningful improvement.

        When studying flexible systems, local sharpening can substantially improve visualization
        of domain organization, but users should remain cautious not to over-interpret weak density.
        If a structural reference is available, it should be used as supportive biological context
        rather than as a substitute for experimental evidence.

        Final Perspective

        For many cryo-EM users, sharpening represents an essential interpretative step between
        reconstruction and biological analysis. Its value lies not simply in making maps look
        clearer, but in making structural information easier to assess, compare, and understand.
        Careful use of local enhancement, appropriate masking, and biologically sensible parameter
        choices can substantially improve the reliability of downstream structural interpretation.
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
