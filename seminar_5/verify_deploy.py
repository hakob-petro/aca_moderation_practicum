"""Mission 3: terminate the server process; replace upstream with controlled faults.

Restores normal Compose configuration in finally, including on Ctrl+C.
The learner owns this Compose project; no other students' resources are touched.
"""
import json
from pathlib import Path
import subprocess
import tempfile
import time

from common import SETUP, config, compose, env, http, SAMPLE

work = Path(config()["gateway"])
settings = env()
url = f"http://127.0.0.1:{settings['PORT']}"
report = {}
report_path = SETUP / "failure.json"
report_path.unlink(missing_ok=True)


def ready():
    for _ in range(60):
        try:
            if http(url + "/healthz", timeout=1)[0] == 200:
                return
        except Exception:
            pass
        time.sleep(1)
    raise RuntimeError("Gateway did not return within 60 seconds")


def call(expected):
    start = time.perf_counter()
    status, body = http(url + "/moderate", settings["GATEWAY_KEY"], SAMPLE, timeout=10)
    seconds = time.perf_counter() - start
    assert status == expected and "decision" not in body, (status, body)
    assert seconds < 5, f"Failure took {seconds:.1f}s; expected < 5s"
    print(f"PASS  HTTP {status} in {seconds:.2f}s, no decision")
    return seconds


cid = compose("ps", "-q", "gateway")
before = json.loads(subprocess.check_output(["docker", "inspect", cid]))[0]
assert before["HostConfig"]["RestartPolicy"]["Name"] == "unless-stopped", "Finish mission 2's restart policy"
# A Docker stop/kill is an operator stop and suppresses the restart policy.
# Signal the server process from inside instead; Docker sees an unexpected exit.
subprocess.run(["docker", "exec", cid, "python", "-c", "import os; os.kill(1, 15)"],
               check=True, capture_output=True)
# Wait for the recorded restart, not just an old connection to /healthz.
for _ in range(60):
    after = json.loads(subprocess.check_output(["docker", "inspect", cid]))[0]
    if after["RestartCount"] > before["RestartCount"] and after["State"]["Running"]:
        break
    time.sleep(1)
else:
    raise RuntimeError("Docker did not restart the terminated gateway process")
ready()
report["restart"] = True
print("PASS  Docker restarted the terminated gateway process")

image = before["Image"]
with tempfile.TemporaryDirectory(prefix="s5-fault-") as tmp:
    override = Path(tmp) / "fault.yml"
    try:
        for mode, expected, label in [("down", 503, "unavailable"), ("slow", 504, "timeout"), ("bad", 502, "malformed")]:
            override.write_text(json.dumps({"services": {
                "gateway": {"environment": {"MODEL_URL": f"http://fault:9000/{mode}/v1", "MODEL_TIMEOUT": "2"}},
                "fault": {"image": image, "entrypoint": ["python", "-c",
                          (Path(__file__).resolve().parent / "fault_server.py").read_text()]}
            }}))
            compose("-f", "compose.yml", "-f", str(override), "up", "-d", "--force-recreate")
            ready()
            report[label + "_seconds"] = round(call(expected), 3)
            report[label] = True
    finally:
        if override.exists():
            compose("-f", "compose.yml", "-f", str(override), "rm", "-s", "-f", "fault")
        compose("up", "-d", "--force-recreate", "gateway")
        ready()
        report["restored"] = True
        report_path.write_text(json.dumps(report, indent=2) + "\n")
        print("Normal upstream configuration restored. Warm the real model with client.py before the load test.")
