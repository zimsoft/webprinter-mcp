#!/usr/bin/env node

const { spawn } = require("node:child_process");

const candidates = process.platform === "win32"
  ? ["python", "py"]
  : ["python3", "python"];

const moduleArgs = ["-m", "webprinter_mcp"];

function runCandidate(index) {
  if (index >= candidates.length) {
    process.stderr.write(
      [
        "Unable to start webprinter-mcp.",
        "A Python 3.10+ runtime is required.",
        "Install the Python package first:",
        "  pip install webprinter-mcp",
      ].join("\n") + "\n"
    );
    process.exit(1);
    return;
  }

  const command = candidates[index];
  const child = spawn(command, moduleArgs, {
    stdio: "inherit",
    env: process.env,
    shell: false,
  });

  child.on("error", () => {
    runCandidate(index + 1);
  });

  child.on("exit", (code, signal) => {
    if (signal) {
      process.kill(process.pid, signal);
      return;
    }
    process.exit(code ?? 0);
  });
}

runCandidate(0);
