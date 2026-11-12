// One test command for the current PostgreSQL application, TP1 and UI logic.
import { spawnSync } from "node:child_process";
import { existsSync, readdirSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

export function testCommands(root) {
  const candidates = [join(root, ".venv", "Scripts", "python.exe"), join(root, ".venv", "bin", "python")];
  const python = candidates.find((candidate) => existsSync(candidate)) || "python";
  const javascriptTests = readdirSync(join(root, "tests"))
    .filter((name) => name.endsWith(".test.mjs")).sort()
    .map((name) => join("tests", name));
  return [
    [python, ["-m", "pytest", "tests", "--ds=tests.settings_postgres", "--reuse-db", "-k", "not test_guard_refuses_unmarked_or_wrong_database", "-q"]],
    [python, ["-m", "pytest", "tests/test_demo_data.py::test_guard_refuses_unmarked_or_wrong_database", "--ds=tests.settings_sqlite_legacy", "-q"]],
    [python, ["-m", "unittest", "discover", "-s", "mcp-server", "-p", "test_*.py", "-v"]],
    [process.execPath, ["--test", ...javascriptTests]],
  ];
}

export function runSuite(root, run = spawnSync) {
  for (const [command, args] of testCommands(root)) {
    const result = run(command, args, { cwd: root, stdio: "inherit" });
    if (result.error) {
      console.error(`Cannot start test command: ${result.error.message}`);
      return 1;
    }
    if (result.status !== 0) return result.status || 1;
  }
  return 0;
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  process.exitCode = runSuite(resolve(dirname(fileURLToPath(import.meta.url)), ".."));
}
