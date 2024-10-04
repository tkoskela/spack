# Copyright 2013-2024 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack.package import *

class Sopt(CMakePackage):
    """SOPT is an open-source C++ package available under the license below. It performs
    Sparse OPTimisation using state-of-the-art convex optimisation algorithms. It solves a
    variety of sparse regularisation problems, including the Sparsity Averaging Reweighted
    Analysis (SARA) algorithm.
    """

    homepage = "https://astro-informatics.github.io/sopt/"
    url = "https://github.com/astro-informatics/sopt/archive/refs/tags/v4.2.0.tar.gz"
    git = "https://github.com/astro-informatics/sopt"

    maintainers("tkoskela", "mmcleod89", "20DM")
    license("GPL-2.0")

    version("4.2.0", sha256="25e579722f8e049d37c9155affa57ec2f38a2f8414c9cf430da2b7bafc86907b")

    variant("tests", default=True, description="Build tests")
    variant("examples", default=True, description="Build examples")
    variant("benchmarks", default=False, description="Build benchmarks")
    variant("openmp", default=False, description="Enable multithreading with OpenMP")
    variant("mpi", default=False, description="Enable parallelisation with MPI")
    variant("docs", default=False, description="Enable multithreading with OpenMP")
    variant("coverage", default=False, description="")
    variant("cppflow", default=False, description="Build with Tensorflow support using cppflow")
    variant("onnxrt", default=False, description="Build with Tensorflow support using onnx")

    depends_on("cmake@3")
    depends_on("eigen@3.4")
    depends_on("libtiff@4.5")
    depends_on("catch2@3.4", when="+tests")
    depends_on("mpi", when="+mpi")
    depends_on("benchmark@1.8", when="+benchmarks")
    depends_on("onnx@1.16", when="+onnxrt")
    depends_on("doxygen@1.9", when="+docs")

    def cmake_args(self):
        args = [
            self.define_from_variant("docs", "docs"),
            self.define_from_variant("examples", "examples"),
            self.define_from_variant("tests", "tests"),
            self.define_from_variant("benchmarks", "benchmarks"),
            self.define_from_variant("openmp", "openmp"),
            self.define_from_variant("dompi", "mpi"),
            self.define_from_variant("onnxrt", "onnxrt"),
            self.define_from_variant("coverage", "coverage"),
        ]
        return args


    def setup_run_environment(self, env):
        if "+tests" in self.spec:
            env.prepend_path("PATH", self.spec.prefix.tests)
        if "+examples" in self.spec:
            env.prepend_path("PATH", join_path(self.spec.prefix, "examples"))
        if "+benchmarks" in self.spec:
            env.prepend_path("PATH", join_path(self.spec.prefix, "benchmarks"))

    def install(self, spec, prefix):
        with working_dir(self.build_directory):
            make("install")
            if "+tests" in spec:
                install_tree("cpp/tests", spec.prefix.tests)
            if "+examples" in spec:
                install_tree("cpp/examples", join_path(spec.prefix, "examples"))
            if "+benchmarks" in spec:
                install_tree("cpp/benchmarks", join_path(spec.prefix, "benchmarks"))
