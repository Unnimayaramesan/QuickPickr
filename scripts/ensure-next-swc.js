/**
 * Ensures @next/swc-* is installed for apps/web in npm workspaces.
 * Next.js optional SWC binaries are often skipped when hoisted; without them
 * Next tries to patch the lockfile and fails with ENOWORKSPACES.
 */
const { execSync } = require("child_process");
const fs = require("fs");
const path = require("path");

const webDir = path.join(__dirname, "..", "apps", "web");
const nextPkg = path.join(webDir, "node_modules", "next", "package.json");

if (!fs.existsSync(nextPkg)) {
  process.exit(0);
}

const nextVersion = JSON.parse(fs.readFileSync(nextPkg, "utf8")).version;
const platformPkgs = {
  darwin: process.arch === "arm64" ? "@next/swc-darwin-arm64" : "@next/swc-darwin-x64",
  linux: "@next/swc-linux-x64-gnu",
  win32: process.arch === "arm64" ? "@next/swc-win32-arm64-msvc" : "@next/swc-win32-x64-msvc",
};

const pkg = platformPkgs[process.platform];
if (!pkg) {
  process.exit(0);
}

const installed = path.join(webDir, "node_modules", pkg);
if (fs.existsSync(installed)) {
  process.exit(0);
}

console.log(`[quickpickr] Installing ${pkg}@${nextVersion} for Next.js (monorepo SWC fix)...`);
try {
  execSync(`npm install ${pkg}@${nextVersion} --no-save --prefix "${webDir}"`, {
    stdio: "inherit",
    env: { ...process.env, npm_config_workspaces: "false" },
  });
} catch {
  console.warn(`[quickpickr] Could not auto-install ${pkg}. Run from apps/web:`);
  console.warn(`  npm install ${pkg}@${nextVersion}`);
}
