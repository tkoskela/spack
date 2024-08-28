# Copyright 2013-2024 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack.package import *


class Seqfu(Package):
    """seqfu - Sequece Fastx Utilities"""

    homepage = "https://github.com/telatin/seqfu2"
    url = "https://github.com/telatin/seqfu2/archive/refs/tags/v1.20.3.tar.gz"

    license("GPL-3.0", checked_by="dialvarezs")

    version("1.20.3", sha256="1b287b99f3f1ac7045f4d551e781d6780ce168ba8e0a7bfaa0f5490f32e15938")

    depends_on("c", type="build")  # generated
    depends_on("cxx", type="build")  # generated

    depends_on("nim@2", type="build")
    depends_on("zlib", type="build")

    patch("wno_incompatible_pointer_types.patch", when="%gcc@14:")

    def setup_build_environment(self, env):
        env.set("NIMBLE_DIR", ".nimble")

    def install(self, spec, prefix):
        nimble = Executable("nimble")
        nimble("install", "-y", "--depsOnly")

        make(parallel=False)
        install_tree("bin", join_path(prefix, "bin"))
