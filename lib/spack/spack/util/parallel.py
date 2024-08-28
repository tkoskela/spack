# Copyright 2013-2024 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)
import concurrent.futures
import multiprocessing
import os
import sys
import traceback
from typing import Optional

from spack.util.cpus import determine_number_of_jobs


class ErrorFromWorker:
    """Wrapper class to report an error from a worker process"""

    def __init__(self, exc_cls, exc, tb):
        """Create an error object from an exception raised from
        the worker process.

        The attributes of the process error objects are all strings
        as they are easy to send over a pipe.

        Args:
            exc: exception raised from the worker process
        """
        self.pid = os.getpid()
        self.error_message = str(exc)
        self.stacktrace_message = "".join(traceback.format_exception(exc_cls, exc, tb))

    @property
    def stacktrace(self):
        msg = "[PID={0.pid}] {0.stacktrace_message}"
        return msg.format(self)

    def __str__(self):
        return self.error_message


class Task:
    """Wrapped task that trap every Exception and return it as an
    ErrorFromWorker object.

    We are using a wrapper class instead of a decorator since the class
    is pickleable, while a decorator with an inner closure is not.
    """

    def __init__(self, func):
        self.func = func

    def __call__(self, *args, **kwargs):
        try:
            value = self.func(*args, **kwargs)
        except Exception:
            value = ErrorFromWorker(*sys.exc_info())
        return value


def imap_unordered(
    f, list_of_args, *, processes: int, maxtaskperchild: Optional[int] = None, debug=False
):
    """Wrapper around multiprocessing.Pool.imap_unordered.

    Args:
        f: function to apply
        list_of_args: list of tuples of args for the task
        processes: maximum number of processes allowed
        debug: if False, raise an exception containing just the error messages
            from workers, if True an exception with complete stacktraces
        maxtaskperchild: number of tasks to be executed by a child before being
            killed and substituted

    Raises:
        RuntimeError: if any error occurred in the worker processes
    """
    if sys.platform in ("darwin", "win32") or len(list_of_args) == 1:
        yield from map(f, list_of_args)
        return

    with multiprocessing.Pool(processes, maxtasksperchild=maxtaskperchild) as p:
        for result in p.imap_unordered(Task(f), list_of_args):
            if isinstance(result, ErrorFromWorker):
                raise RuntimeError(result.stacktrace if debug else str(result))
            yield result


class SequentialExecutor(concurrent.futures.Executor):
    """Executor that runs tasks sequentially in the current thread."""

    def submit(self, fn, *args, **kwargs):
        """Submit a function to be executed."""
        future = concurrent.futures.Future()
        try:
            future.set_result(fn(*args, **kwargs))
        except Exception as e:
            future.set_exception(e)
        return future


def make_concurrent_executor() -> concurrent.futures.Executor:
    """Can't use threading because it's unsafe, and can't use spawned processes because of globals.
    That leaves only forking."""
    if multiprocessing.get_start_method() == "fork":
        return concurrent.futures.ProcessPoolExecutor(determine_number_of_jobs(parallel=True))
    return SequentialExecutor()
