// Pulls every run for a set of tasks since a cutoff, with goal verdicts and transcripts, into one JSON file.
// Usage: bun pull-runs.ts --scope <org>/<product> --tasks <taskId[,taskId...]> --since <ISO time> --out runs.json
// Pages per task (the unfiltered run list hides iteration runs and caps at 20), retries with backoff,
// and reports runs it could not fetch as DATA UNAVAILABLE instead of dropping or zeroing them.
import { $ } from "bun";

const arg = (k: string) => { const i = process.argv.indexOf(`--${k}`); return i > 0 ? process.argv[i + 1] : undefined; };
const scope = arg("scope"), tasks = arg("tasks")?.split(",").filter(Boolean) ?? [], since = Date.parse(arg("since") ?? "1970-01-01"), out = arg("out") ?? "runs.json";
if (!scope || !tasks.length) throw new Error("usage: bun pull-runs.ts --scope <org>/<product> --tasks <id,id> --since <ISO> --out runs.json");

// tpc may append a CLI-update notice after the JSON on stdout; parse only the JSON value.
const parse = (t: string) => JSON.parse(t.slice(t.search(/[[{]/), Math.max(t.lastIndexOf("}"), t.lastIndexOf("]")) + 1));
const rowsOf = (d: any) => (Array.isArray(d) ? d : d?.runs ?? d?.data ?? d?.items ?? []);
async function tpc(args: string[]) {
  for (let a = 0; a < 6; a++) {
    const r = await $`tpc ${args} --scope ${scope} --format json`.quiet().nothrow();
    try { if (r.exitCode === 0) return parse(r.stdout.toString()); } catch {}
    await Bun.sleep(8000 * (a + 1)); // 429s and empty bodies are common under load
  }
  return null;
}

const listed: any[] = [];
for (const taskId of tasks) {
  for (let page = 1; page < 50; page++) {
    const d = await tpc(["sim", "run", "list", "--task-id", taskId, "--page-size", "100", "--page", String(page)]);
    if (!d) { console.error(`DATA UNAVAILABLE: run list for task ${taskId} page ${page}`); break; }
    const rows = rowsOf(d); listed.push(...rows.filter((r: any) => Date.parse(r.createdAt) >= since));
    if (rows.length < 100) break;
    await Bun.sleep(2500);
  }
}

const runs: any[] = [];
for (const r of listed) {
  const d = await tpc(["sim", "run", "get", r.id]);
  runs.push(d ? { ...d, events: d.agentOutput?.events ?? [], agentOutput: undefined } : { id: r.id, taskId: r.taskId, environmentId: r.environmentId, status: r.status, unavailable: true });
  await Bun.sleep(2500);
}
await Bun.write(out, JSON.stringify(runs));
const unavailable = runs.filter((x) => x.unavailable).length;
console.log(`runs listed ${listed.length}, fetched ${runs.length - unavailable}, DATA UNAVAILABLE ${unavailable} -> ${out}`);
