"""Your first function on a cloud GPU, on Modal.

    modal run hello_modal.py

Modal starts a machine with a GPU, runs hello() on it, and shuts it down when
it returns. You pay only for those seconds. hello() also writes a file to the
Modal volume "aca-models", a disk in Modal's cloud that outlives the machine:
your trained models will live there in Session 4.
"""

import modal

app = modal.App("aca-hello-gpu")

# The same packages as modal_score.py, so Modal builds them once and reuses them there.
image = modal.Image.debian_slim(python_version="3.12").uv_pip_install(
    "torch==2.14.1", "transformers==5.20.2"
)
models = modal.Volume.from_name("aca-models", create_if_missing=True)


# The first GPU type in this list that Modal has free right now.
@app.function(gpu=["L4", "A10", "T4"], image=image, volumes={"/models": models}, timeout=300)
def hello(name: str) -> str:
    import datetime
    import time

    import torch

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
        f"hello_from={name}\n"
        f"ran_on=Modal\n"
        f"gpu={gpu}\n"
        f"gpu_memory_gb={memory_gb:.1f}\n"
        f"matmul_cpu_ms={cpu_ms:.0f}\n"
        f"matmul_gpu_ms={gpu_ms:.1f}\n"
        f"written_at={datetime.datetime.now(datetime.timezone.utc):%Y-%m-%d %H:%M:%S} UTC\n"
    )
    with open("/models/hello.txt", "w") as f:
        f.write(report)
    models.commit()  # save the file to the volume now, not only when the machine stops
    return report


@app.local_entrypoint()
def main():
    import getpass

    print(hello.remote(getpass.getuser()))
    print("Saved as hello.txt in the Modal volume aca-models.")
