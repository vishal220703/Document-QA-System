const { execFileSync } = require("node:child_process");
const os = require("node:os");

const ports = [3000, 8000];
const processIds = new Set();

function collectWindowsProcessIds(port) {
  try {
    const output = execFileSync("netstat", ["-ano", "-p", "tcp"], {
      encoding: "utf8",
    });
    for (const line of output.split(/\r?\n/)) {
      const match = line.match(
        new RegExp(
          `\\s+(?:TCP)\\s+[^\\s]+:${port}\\s+[^\\s]+\\s+LISTENING\\s+(\\d+)`,
          "i",
        ),
      );
      if (match) processIds.add(match[1]);
    }
  } catch {
    // No matching listener or netstat unavailable.
  }
}

function collectUnixProcessIds(port) {
  try {
    const output = execFileSync("lsof", ["-ti", `tcp:${port}`], {
      encoding: "utf8",
    });
    for (const processId of output.split(/\r?\n/).filter(Boolean))
      processIds.add(processId.trim());
  } catch {
    // No matching listener or lsof unavailable.
  }
}

for (const port of ports) {
  if (os.platform() === "win32") collectWindowsProcessIds(port);
  else collectUnixProcessIds(port);
}

for (const processId of processIds) {
  try {
    if (os.platform() === "win32") {
      execFileSync("taskkill", ["/PID", processId, "/T", "/F"], {
        stdio: "ignore",
      });
    } else {
      process.kill(Number(processId), "SIGTERM");
    }
  } catch {
    // The process may have exited between discovery and termination.
  }
}
