// Lance un script shell (.sh) ou Python (.py) du dépôt, quel que soit le système : c'est par lui que passent
// les scripts du package.json (npm utilise cmd.exe sous Windows, qui ne sait pas lancer un script shell).
//   node tools/lancer.mjs infra/ci/images.sh version
//   node tools/lancer.mjs tools/boutique.py demarrer
// Sous Windows, le shell est celui de Git for Windows, et la conversion automatique des chemins de Git Bash
// est désactivée (MSYS_NO_PATHCONV) pour que les chemins passés à Docker restent intacts.
import { execFileSync, spawnSync } from "node:child_process";
import { existsSync } from "node:fs";
import path from "node:path";

const [script, ...args] = process.argv.slice(2);
const windows = process.platform === "win32";

function shellDeGit() {
  // git --exec-path → C:/Program Files/Git/mingw64/libexec/git-core
  const execPath = execFileSync("git", ["--exec-path"], { encoding: "utf8" }).trim();
  const racineGit = path.resolve(execPath, "..", "..", "..");
  const sh = [path.join(racineGit, "bin", "sh.exe"), path.join(racineGit, "usr", "bin", "sh.exe")].find(existsSync);
  if (!sh) throw new Error(`sh introuvable dans ${racineGit} : installer Git for Windows`);
  return sh;
}

let interpreteur;
if (script?.endsWith(".sh")) interpreteur = windows ? shellDeGit() : "sh";
else if (script?.endsWith(".py")) interpreteur = windows ? "python" : "python3";
else {
  console.error("Usage : node tools/lancer.mjs <script.sh|script.py> [arguments]");
  process.exit(2);
}

const r = spawnSync(interpreteur, [script, ...args], {
  stdio: "inherit",
  env: { ...process.env, MSYS_NO_PATHCONV: "1" },
});
if (r.error) {
  console.error(r.error.message);
  process.exit(1);
}
process.exit(r.status ?? 1);
