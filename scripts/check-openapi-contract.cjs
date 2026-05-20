"use strict";

/** Minimal contract gate: OpenAPI snapshot exists and is non-empty (expand with parsing later). */

const fs = require("fs");
const path = require("path");

const p = path.join(__dirname, "..", "packages", "api-contract", "openapi.yaml");
if (!fs.existsSync(p)) {
  console.error("Missing:", p);
  process.exit(1);
}
const st = fs.statSync(p);
if (st.size < 50) {
  console.error("openapi.yaml looks empty:", p);
  process.exit(1);
}
console.log("OK:", p, `(${st.size} bytes)`);
