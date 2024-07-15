# Copyright 2013-2024 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack.package import *

class Purify(CMakePackage):
    """PURIFY is an open-source collection of routines written in C++ available under the 
    license below. It implements different tools and high-level to perform radio interferometric 
    imaging, i.e. to recover images from the Fourier measurements taken by radio interferometric 
    telescopes.
    """

    homepage = "https://astro-informatics.github.io/purify/"
    url = "https://github.com/astro-informatics/purify/archive/refs/tags/v4.1.0.tar.gz"
    git = "https://github.com/astro-informatics/purify"

    maintainers("tkoskela", "mmcleod89", "20DM")
    license("GPL-2.0")

    version("debug", branch="tk/spack-install-fixes")
    version("develop", branch="develop")
    version("4.1.0", sha256="716b1dfb640b48e8825709e254e4e65a6d65eb00698b2489653b2d4b2c4cb346")

    variant("tests", default=True, description="Build tests")
    variant("openmp", default=True, description="Enable multithreading with OpenMP")
    variant("mpi", default=True, description="Enable parallelisation with MPI")
    variant("logging", default=True, description="Enable logging")
    variant("examples", default=False, description="Build examples")
    variant("benchmarks", default=False, description="Build benchmarks")
    variant("docs", default=False, description="Enable multithreading with OpenMP")
    variant("coverage", default=False, description="")
    variant("af", default=False, description="Enable ArrayFire")
    variant("cimg", default=False, description="Enable Cimg")
    variant("casa", default=False, description="Enable Casacore")
    variant("cppflow", default=False, description="Build with Tensorflow support using cppflow")
    variant("onnxrt", default=False, description="Build with Tensorflow support using onnx")

    depends_on("cmake")
    depends_on("eigen@3.4")
    depends_on("libtiff@4.5")
    depends_on("fftw-api")
    depends_on("yaml-cpp@0.7")
    depends_on("boost@1.82")
    depends_on("cfitsio@4.2")
    depends_on("cubature@1.0")
    depends_on("sopt@4.1.0")
    depends_on("catch2@3.4", when="+tests")
    depends_on("mpi", when="+mpi")
    depends_on("benchmark@=1.8.2~performance_counters", when="+benchmarks")
    depends_on("onnx@1.16", when="+onnxrt")
    depends_on("doxygen@1.9", when="+docs")
    #depends_on("cimg@3.0", when="+cimg")
    depends_on("casacore", when="+casa")
    depends_on("arrayfire", when="+af")
    depends_on("spdlog@1.12", when="+logging")

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
            self.define_from_variant("cppflow", "cppflow"),
            self.define_from_variant("logging", "logging"),
            self.define_from_variant("doaf", "af"),
            self.define_from_variant("docasa", "casa"),
            self.define_from_variant("docimg", "cimg")
        ]
        return args

    def install(self, spec, prefix):
        with working_dir(self.build_directory):
            make("install")
            # if "+tests" in spec or "+examples" in spec or "benchmarks" in spec:
            #     install_tree("cpp", join_path(spec.prefix, 'cpp'))
            if "+tests" in spec:
                install_tree("cpp/tests", spec.prefix.tests)
                install_tree("data", join_path(spec.prefix, "data"))
            if "+benchmarks" in spec:
                install_tree("cpp/benchmarks", join_path(spec.prefix, "benchmarks"))

