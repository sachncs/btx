# Copyright (c) 2026 Sachin
# SPDX-License-Identifier: MIT
"""Multi-process PSBT processing pipeline.

Provides :func:`process_psbt_batch` for parsing multiple PSBT files in
parallel (with ``ProcessPoolExecutor`` for CPU-bound work) and
:func:`process_psbt_batch_with` for parsing and then applying a
caller-supplied transform to each result.

Both functions return a :class:`~btx.signature.pipeline.BatchResult`
aggregating the successfully parsed PSBTs alongside any errors, so a
single malformed file does not abort the whole batch.  Each batch is
tagged with a short request ID (UUID4 first 12 hex digits) for log
correlation.

The worker function :func:`parse_psbt_worker` is intentionally
defined at module scope so it can be pickled and dispatched across
process boundaries by :class:`concurrent.futures.ProcessPoolExecutor`.
"""

from __future__ import annotations

import logging
import uuid
from collections.abc import Callable, Sequence
from concurrent.futures import ProcessPoolExecutor, as_completed

from btx.psbt.models import Psbt
from btx.psbt.parser import parse_psbt_from_file
from btx.signature.pipeline import BatchResult

logger = logging.getLogger(__name__)


def parse_psbt_worker(path: str) -> Psbt | tuple[str, str]:
    """Module-level worker for ``ProcessPoolExecutor``.

    Must live at module scope (not as a nested function) so the
    executor can pickle it for dispatch to worker processes.  Each
    invocation parses a single PSBT file; any exception is captured
    into a ``(path, error_message)`` tuple so the parent process can
    attribute failures without aborting the batch.

    Args:
        path: Path to a PSBT file.

    Returns:
        The parsed :class:`Psbt`, or a ``(path, error_message)``
        tuple if parsing failed.
    """
    try:
        return parse_psbt_from_file(path)
    except Exception as exc:
        return (path, str(exc))


def process_psbt_batch(
    paths: Sequence[str],
    *,
    max_workers: int = 1,
    request_id: str | None = None,
) -> BatchResult[Psbt]:
    """Parse multiple PSBT files, optionally in parallel.

    Args:
        paths: Sequence of file paths to PSBT files.
        max_workers: Maximum number of worker processes (``1`` for
            sequential).
        request_id: Optional correlation ID for logging.

    Returns:
        A ``BatchResult`` aggregating all parsed PSBTs and errors.
    """
    rid = request_id or uuid.uuid4().hex[:12]
    logger.info(
        "[%s] Processing %d PSBT files (%d workers).", rid, len(paths), max_workers
    )

    all_psbts: list[Psbt] = []
    errors: list[tuple[str, str]] = []

    if max_workers <= 1:
        for path in paths:
            try:
                all_psbts.append(parse_psbt_from_file(path))
            except Exception as exc:
                logger.warning("[%s] Failed to parse %s: %s", rid, path, exc)
                errors.append((path, str(exc)))
    else:
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            fut_map = {executor.submit(parse_psbt_worker, p): p for p in paths}
            for future in as_completed(fut_map):
                path = fut_map[future]
                try:
                    worker_result = future.result()
                except Exception as exc:
                    logger.warning("[%s] Worker exception for %s: %s", rid, path, exc)
                    errors.append((path, str(exc)))
                    continue
                if isinstance(worker_result, tuple):
                    errors.append(worker_result)
                else:
                    all_psbts.append(worker_result)

    batch_result = BatchResult[Psbt](
        items=tuple(all_psbts),
        errors=tuple(errors),
    )
    logger.info(
        "[%s] PSBT batch complete: %d / %d successful.",
        rid,
        batch_result.successful,
        batch_result.total,
    )
    return batch_result


def process_psbt_batch_with(
    paths: Sequence[str],
    transform: Callable[[Psbt], Psbt],
    *,
    max_workers: int = 1,
    request_id: str | None = None,
) -> BatchResult[Psbt]:
    """Parse and transform multiple PSBTs in parallel.

    *transform* is called on each successfully parsed PSBT and may
    perform operations such as signing or finalization.

    Args:
        paths: Sequence of file paths.
        transform: A callable that receives a ``Psbt`` and returns a
            (possibly modified) ``Psbt``.
        max_workers: Worker process count (``1`` for sequential).
        request_id: Optional correlation ID.

    Returns:
        A ``BatchResult`` with the transformed Psbts.
    """
    raw = process_psbt_batch(paths, max_workers=max_workers, request_id=request_id)
    transformed: list[Psbt] = []
    new_errors: list[tuple[str, str]] = list(raw.errors)
    for psbt in raw.items:
        try:
            transformed.append(transform(psbt))
        except Exception as exc:
            logger.warning("Transform failed for one PSBT: %s", exc)
            new_errors.append(("<transform>", str(exc)))
    return BatchResult[Psbt](
        items=tuple(transformed),
        errors=tuple(new_errors),
    )


__all__ = [
    "process_psbt_batch",
    "process_psbt_batch_with",
]
