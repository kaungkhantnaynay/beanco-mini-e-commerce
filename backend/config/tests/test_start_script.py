import os
import subprocess
from pathlib import Path

import pytest


@pytest.mark.parametrize(
    ("runtime_port", "expected_binding"),
    [("10000", "0.0.0.0:10000"), (None, "0.0.0.0:8000")],
)
def test_start_script_uses_runtime_port_with_local_default(
    tmp_path: Path,
    runtime_port: str | None,
    expected_binding: str,
) -> None:
    backend_dir = Path(__file__).resolve().parents[2]
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    fake_gunicorn = fake_bin / "gunicorn"
    fake_gunicorn.write_text('#!/bin/sh\nprintf \'%s\\n\' "$@" > "$CAPTURE_PATH"\n')
    fake_gunicorn.chmod(0o755)
    captured_arguments = tmp_path / "gunicorn-arguments"
    environment = {
        **os.environ,
        "PATH": f"{fake_bin}:{os.environ['PATH']}",
        "CAPTURE_PATH": str(captured_arguments),
    }
    if runtime_port is None:
        environment.pop("PORT", None)
    else:
        environment["PORT"] = runtime_port
    environment.pop("SEED_CATALOG_ON_START", None)

    subprocess.run(  # noqa: S603
        ["/bin/sh", "scripts/start.sh"],
        cwd=backend_dir,
        env=environment,
        check=True,
    )

    assert captured_arguments.read_text().splitlines() == [
        "config.wsgi:application",
        "--bind",
        expected_binding,
        "--workers",
        "2",
        "--timeout",
        "30",
        "--error-logfile",
        "-",
    ]


def test_start_script_seeds_catalog_when_enabled(tmp_path: Path) -> None:
    backend_dir = Path(__file__).resolve().parents[2]
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    captured_seed_arguments = tmp_path / "seed-arguments"
    fake_python = fake_bin / "python"
    fake_python.write_text('#!/bin/sh\nprintf \'%s\\n\' "$@" > "$SEED_CAPTURE_PATH"\n')
    fake_python.chmod(0o755)
    fake_gunicorn = fake_bin / "gunicorn"
    fake_gunicorn.write_text("#!/bin/sh\nexit 0\n")
    fake_gunicorn.chmod(0o755)

    subprocess.run(  # noqa: S603
        ["/bin/sh", "scripts/start.sh"],
        cwd=backend_dir,
        env={
            **os.environ,
            "PATH": f"{fake_bin}:{os.environ['PATH']}",
            "SEED_CATALOG_ON_START": "true",
            "SEED_CAPTURE_PATH": str(captured_seed_arguments),
        },
        check=True,
    )

    assert captured_seed_arguments.read_text().splitlines() == ["manage.py", "seed_catalog"]
