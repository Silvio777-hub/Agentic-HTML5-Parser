"""
parallel_runner.py — Concurrent execution helper for AI agents.

Pipeline overview
-----------------
The overall agent pipeline is partially ordered:

    Spec → Codegen → [CritiqueAgentAI || RedTeamAgentAI] → Test → Monitor → Repair

Sequential stages (must run one after the other):
    1. SpecAgent          — produces the HTML5 specification from user input.
    2. CodegenAgent       — generates parser code from the specification.
    3. TestAgent          — runs the test-suite against the generated code.
    4. MonitorAgent       — inspects metrics / coverage from the test run.
    5. RepairAgent        — fixes failures reported by Monitor/Test.

Parallel stage (both agents need only the generated code as input):
    • CritiqueAgentAI  — reviews code quality, correctness, and spec compliance.
    • RedTeamAgentAI   — adversarially probes the parser for edge-case failures.

    Because neither agent depends on the other's output they can be dispatched
    concurrently via ``run_agents_parallel``, cutting wall-clock time roughly
    in half for this stage.

How to use
----------
Wrap each call with ``functools.partial`` so that the callable takes **no**
arguments before passing it to ``run_agents_parallel``:

    import functools
    from src.parallel_runner import run_agents_parallel
    from src.agents import CritiqueAgentAI, RedTeamAgentAI

    critique_agent = CritiqueAgentAI(...)
    red_team_agent = RedTeamAgentAI(...)

    critique_fn = functools.partial(critique_agent.run, generated_code)
    red_team_fn = functools.partial(red_team_agent.run, generated_code)

    critique_result, red_team_result = run_agents_parallel(
        [critique_fn, red_team_fn],
        timeout=120,
    )
"""

import functools
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError as FuturesTimeoutError
from typing import Any, Callable, List


def run_agents_parallel(agent_funcs: List[Callable[[], Any]], timeout: int = 120) -> List[Any]:
    """Run a list of callables in parallel using a thread pool.

    Each callable **must take no arguments** — use ``functools.partial`` to
    bind any required arguments before passing the callable here.

    The results are returned in the **same order** as ``agent_funcs``,
    regardless of the order in which the threads finish.

    Parameters
    ----------
    agent_funcs:
        List of zero-argument callables to execute concurrently.
    timeout:
        Maximum number of seconds to wait for *all* tasks to complete.
        If any task exceeds this limit a ``TimeoutError`` is raised.

    Returns
    -------
    list
        Results in the same order as ``agent_funcs``.

    Raises
    ------
    TimeoutError
        If one or more tasks do not finish within ``timeout`` seconds.
    Exception
        Re-raises the first exception thrown by any agent callable.
    """
    # Allocate a fixed-size results list indexed by the original call order.
    # This guarantees that outputs match agent_funcs ordering regardless of completion order.
    results: List[Any] = [None] * len(agent_funcs)

    # Dispatch tasks using Python's concurrent ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=len(agent_funcs)) as executor:
        # Submit each agent callable to the worker pool and track its original index.
        # future_to_index maps each Future instance back to its position (0 to N-1).
        future_to_index = {
            executor.submit(fn): idx
            for idx, fn in enumerate(agent_funcs)
        }

        try:
            # Yield completed futures as soon as they finish execution (as_completed).
            # The timeout parameter enforces a strict global ceiling on stage wall-clock time.
            for future in as_completed(future_to_index, timeout=timeout):
                # Retrieve the original input index for this completed future
                idx = future_to_index[future]
                
                # future.result() retrieves the return value or re-raises any exception thrown inside the worker thread
                results[idx] = future.result()
        except FuturesTimeoutError:
            # Handle timeout breach gracefully by raising a descriptive TimeoutError
            raise TimeoutError(
                f"run_agents_parallel: one or more agents did not finish "
                f"within the {timeout}s timeout."
            )

    # Return ordered list of results matching the input callables
    return results


# ---------------------------------------------------------------------------
# Demo / smoke-test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import time

    def dummy_critique(code: str) -> str:
        """Simulate CritiqueAgentAI taking ~0.5 s."""
        time.sleep(0.5)
        return f"[CritiqueAgentAI] Code looks good: {code!r}"

    def dummy_red_team(code: str) -> str:
        """Simulate RedTeamAgentAI taking ~0.4 s."""
        time.sleep(0.4)
        return f"[RedTeamAgentAI] No critical vulnerabilities found in: {code!r}"

    sample_code = "<html><body><p>Hello, World!</p></body></html>"

    critique_fn = functools.partial(dummy_critique, sample_code)
    red_team_fn = functools.partial(dummy_red_team, sample_code)

    print("Running CritiqueAgentAI and RedTeamAgentAI in parallel …")
    start = time.perf_counter()
    results = run_agents_parallel([critique_fn, red_team_fn], timeout=30)
    elapsed = time.perf_counter() - start

    for result in results:
        print(result)

    print(f"\nCompleted in {elapsed:.2f}s (would have taken ~0.9s sequentially).")
