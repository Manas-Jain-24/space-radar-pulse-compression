"""Publish complete artifacts without truncating files open in previewers."""
from contextlib import contextmanager
from pathlib import Path
import os
import tempfile
import time


@contextmanager
def atomic_output(destination):
    destination = Path(destination).resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    descriptor, name = tempfile.mkstemp(prefix=".radar-", suffix=destination.suffix,
                                      dir=destination.parent)
    os.close(descriptor)
    temporary = Path(name)
    try:
        yield temporary
        for attempt in range(10):
            try:
                os.replace(temporary, destination)
                break
            except OSError:
                if attempt == 9:
                    raise
                time.sleep(0.1)
    finally:
        temporary.unlink(missing_ok=True)


def save_figure(figure, destination, **kwargs):
    with atomic_output(destination) as temporary:
        figure.savefig(temporary, **kwargs)
