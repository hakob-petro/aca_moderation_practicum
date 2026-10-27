# /// script
# requires-python = ">=3.10"
# dependencies = ["torch==2.14.1"]
# ///
"""Your first program on your own GPU.

    uv run hello_gpu.py

Finds the GPU in this machine, multiplies two big matrices on the CPU and on
the GPU, and saves what it found in ~/s3/hello.txt.
"""

import datetime
import getpass
import sys
import time
from pathlib import Path

import torch


def main() -> None:
    if not torch.cuda.is_available():
        sys.exit("No GPU found on this machine. Run nvidia-smi: does it list one?")

    gpu = torch.cuda.get_device_name(0)
    memory_gb = torch.cuda.get_device_properties(0).total_memory / 1e9

    # The same work twice: multiply two 4096 x 4096 matrices, on the CPU and on the GPU.
    a = torch.randn(4096, 4096)
    b = torch.randn(4096, 4096)
    start = time.perf_counter()
    a @ b
    cpu_ms = (time.perf_counter() - start) * 1000

    a, b = a.cuda(), b.cuda()
    a @ b  # the first run on a GPU includes start-up costs
    torch.cuda.synchronize()
    start = time.perf_counter()
    a @ b
    torch.cuda.synchronize()
    gpu_ms = (time.perf_counter() - start) * 1000

    report = (
        f"hello_from={getpass.getuser()}\n"
        f"ran_on=this machine\n"
        f"gpu={gpu}\n"
        f"gpu_memory_gb={memory_gb:.1f}\n"
        f"matmul_cpu_ms={cpu_ms:.0f}\n"
        f"matmul_gpu_ms={gpu_ms:.1f}\n"
        f"written_at={datetime.datetime.now(datetime.timezone.utc):%Y-%m-%d %H:%M:%S} UTC\n"
    )
    out = Path.home() / "s3" / "hello.txt"
    out.parent.mkdir(exist_ok=True)
    out.write_text(report)
    print(report + f"Saved to {out}")


if __name__ == "__main__":
    main()
