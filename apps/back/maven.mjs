// Lance le Maven Wrapper du backend quel que soit le système (mvnw sous Linux/macOS, mvnw.cmd sous Windows) :
// les tâches turbo « build » et « test » fonctionnent ainsi sans Maven installé sur le poste.
import { spawnSync } from "node:child_process";

const windows = process.platform === "win32";
const r = spawnSync(windows ? "mvnw.cmd" : "./mvnw", ["-B", "-ntp", ...process.argv.slice(2)], {
  stdio: "inherit",
  shell: windows,
});
process.exit(r.status ?? 1);
