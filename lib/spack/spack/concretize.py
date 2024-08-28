# Copyright 2013-2024 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)
"""
(DEPRECATED) Used to contain the code for the original concretizer
"""
from contextlib import contextmanager
from itertools import chain

import spack.compilers
import spack.config
import spack.environment
import spack.error
import spack.platforms
import spack.repo
import spack.spec
import spack.target
import spack.tengine
import spack.util.path


class Concretizer:
    """(DEPRECATED) Only contains logic to enable/disable compiler existence checks."""

    #: Controls whether we check that compiler versions actually exist
    #: during concretization. Used for testing and for mirror creation
    check_for_compiler_existence = None

    def __init__(self):
        if Concretizer.check_for_compiler_existence is None:
            Concretizer.check_for_compiler_existence = not spack.config.get(
                "config:install_missing_compilers", False
            )


@contextmanager
def disable_compiler_existence_check():
    saved = Concretizer.check_for_compiler_existence
    Concretizer.check_for_compiler_existence = False
    yield
    Concretizer.check_for_compiler_existence = saved


@contextmanager
def enable_compiler_existence_check():
    saved = Concretizer.check_for_compiler_existence
    Concretizer.check_for_compiler_existence = True
    yield
    Concretizer.check_for_compiler_existence = saved


def find_spec(spec, condition, default=None):
    """Searches the dag from spec in an intelligent order and looks
    for a spec that matches a condition"""
    # First search parents, then search children
    deptype = ("build", "link")
    dagiter = chain(
        spec.traverse(direction="parents", deptype=deptype, root=False),
        spec.traverse(direction="children", deptype=deptype, root=False),
    )
    visited = set()
    for relative in dagiter:
        if condition(relative):
            return relative
        visited.add(id(relative))

    # Then search all other relatives in the DAG *except* spec
    for relative in spec.root.traverse(deptype="all"):
        if relative is spec:
            continue
        if id(relative) in visited:
            continue
        if condition(relative):
            return relative

    # Finally search spec itself.
    if condition(spec):
        return spec

    return default  # Nothing matched the condition; return default.


def concretize_specs_together(*abstract_specs, **kwargs):
    """Given a number of specs as input, tries to concretize them together.

    Args:
        tests (bool or list or set): False to run no tests, True to test
            all packages, or a list of package names to run tests for some
        *abstract_specs: abstract specs to be concretized, given either
            as Specs or strings

    Returns:
        List of concretized specs
    """
    import spack.solver.asp

    allow_deprecated = spack.config.get("config:deprecated", False)
    solver = spack.solver.asp.Solver()
    result = solver.solve(
        abstract_specs, tests=kwargs.get("tests", False), allow_deprecated=allow_deprecated
    )
    return [s.copy() for s in result.specs]


class UnavailableCompilerVersionError(spack.error.SpackError):
    """Raised when there is no available compiler that satisfies a
    compiler spec."""

    def __init__(self, compiler_spec, arch=None):
        err_msg = "No compilers with spec {0} found".format(compiler_spec)
        if arch:
            err_msg += " for operating system {0} and target {1}.".format(arch.os, arch.target)

        super().__init__(
            err_msg,
            "Run 'spack compiler find' to add compilers or "
            "'spack compilers' to see which compilers are already recognized"
            " by spack.",
        )
