"use strict";

/**
 * Run FastAPI query service with PYTHONPATH scoped to apps/query-service.
 * Used by root `npm run dev` alongside Next.js (see package.json).
 */

const { spawn } = require("child_process");
const path = require("path");

const cwd = path.join(__dirname, "..", "apps", "query-service");
const python = process.env.PYTHON || "python";

const child = spawn(
  python,
  ["-m", "uvicorn", "app.main:app", "--reload", "--host", "127.0.0.1", "--port", "8080"],
  {
    cwd,
    env: { ...process.env, PYTHONPATH: cwd },
    stdio: "inherit",
    // Avoid shell:true + args (Node DEP0190); `python` / `py` should be on PATH.
    shell: false,
  },
);

child.on("exit", (code) => process.exit(code === null ? 1 : code));
