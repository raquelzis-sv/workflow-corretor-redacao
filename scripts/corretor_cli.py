#!/usr/bin/env python
"""CLI wrapper for the Correção de Redação workflow.

Usage:
    python -m scripts.corretor_cli <redacao_path> <tema_path_or_text>

The wrapper reads the workflow definition from `.agents/workflows/corretor.md`
(and could be extended to a full workflow engine). For now it simply forwards
the arguments to the existing orchestrator `scripts.process_redacao` which
performs all the steps – text extraction, LLM calls, deterministic score
calculation and markdown report generation.
"""

import sys
import subprocess
from pathlib import Path

def main() -> None:
    if len(sys.argv) != 3:
        print(
            "Usage: python -m scripts.corretor_cli <redacao_path> <tema_path_or_text>",
            file=sys.stderr,
        )
        sys.exit(1)

    redacao = Path(sys.argv[1])
    tema = Path(sys.argv[2])

    # Resolve absolute paths for clarity in logs
    redacao_abs = redacao.resolve()
    tema_abs = tema.resolve()

    # Verify files exist
    if not redacao_abs.is_file():
        print(f"[ERROR] Redação file not found: {redacao_abs}", file=sys.stderr)
        sys.exit(1)
    if not tema_abs.is_file():
        print(f"[ERROR] Tema file not found: {tema_abs}", file=sys.stderr)
        sys.exit(1)

    # Call the existing orchestrator script
    cmd = [
        sys.executable,
        "-m",
        "scripts.process_redacao",
        str(redacao_abs),
        str(tema_abs),
    ]
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Workflow execution failed (exit {e.returncode})", file=sys.stderr)
        sys.exit(e.returncode)

if __name__ == "__main__":
    main()
