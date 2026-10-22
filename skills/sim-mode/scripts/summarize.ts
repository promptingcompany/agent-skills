// Per task x environment cell summary of a pull-runs.ts file.
// Usage: bun summarize.ts runs.json [--adjust adjust.json] [--names names.json] [--md]
//   adjust.json: [{ "run": "<run-id or prefix>", "goal": "<goal name>", "reason": "fixture contamination: ..." }]
//     marks that goal as passed for that run in the ADJUSTED column only; every adjustment needs a reason.
//   names.json: { "<taskId or envId>": "short name" } for readable rows.
// Correctness = every goal whose name does not contain "recorded". Recorded goals are counted separately.
// Infrastructure failures (no goal results, status not completed) are listed and excluded from rates.

const [file] = process.argv.slice(2).filter((a) => !a.startsWith("--") && a.endsWith(".json"));
const opt = (k: string) => { const i = process.argv.indexOf(`--${k}`); return i > 0 ? process.argv[i + 1] : undefined; };
const runs: any[] = await Bun.file(file).json();
const adjust: any[] = opt("adjust") ? await Bun.file(opt("adjust")!).json() : [];
const names: Record<string, string> = opt("names") ? await Bun.file(opt("names")!).json() : {};
const name = (id: string) => names[id] ?? id.slice(0, 8);
for (const a of adjust) if (!a.reason) throw new Error(`adjustment for ${a.run} has no reason`);

function wilson(k: number, n: number, z = 1.96) {
  if (!n) return [0, 0];
  const p = k / n, d = 1 + (z * z) / n, c = p + (z * z) / (2 * n), h = z * Math.sqrt((p * (1 - p)) / n + (z * z) / (4 * n * n));
  return [Math.round(((c - h) / d) * 100), Math.round(((c + h) / d) * 100)];
}
const median = (xs: number[]) => { if (!xs.length) return null; const s = [...xs].sort((a, b) => a - b), m = s.length >> 1; return s.length % 2 ? s[m] : (s[m - 1] + s[m]) / 2; };
const quart = (xs: number[], q: number) => { if (!xs.length) return null; const s = [...xs].sort((a, b) => a - b); return s[Math.min(s.length - 1, Math.floor(q * (s.length - 1)))]; };

const infra = runs.filter((r) => r.status !== "completed" || !(r.goalResults ?? []).length);
const done = runs.filter((r) => !infra.includes(r));
const cells = new Map<string, any>();
for (const r of done) {
  const key = `${name(r.taskId)}|${name(r.environmentId)}`;
  const c = cells.get(key) ?? { n: 0, raw: 0, adj: 0, rec: 0, recN: 0, okTimes: [] as number[], cost: 0 };
  const corr = r.goalResults.filter((g: any) => !/recorded/i.test(g.goalName));
  const rec = r.goalResults.filter((g: any) => /recorded/i.test(g.goalName));
  const adjusted = (g: any) => g.passed || adjust.some((a) => r.id.startsWith(a.run) && a.goal === g.goalName);
  const okRaw = corr.every((g: any) => g.passed), okAdj = corr.every(adjusted);
  c.n++; c.raw += +okRaw; c.adj += +okAdj; c.rec += rec.filter((g: any) => g.passed).length; c.recN += rec.length; c.cost += r.costUsd ?? 0;
  if (okAdj && r.duration) c.okTimes.push(r.duration / 1000);
  cells.set(key, c);
}

const rows = [...cells.entries()].sort(([a], [b]) => a.localeCompare(b)).map(([k, c]) => {
  const [task, env] = k.split("|"), [lo, hi] = wilson(c.adj, c.n);
  return { task, env, asScored: `${c.raw}/${c.n}`, adjusted: `${c.adj}/${c.n}`, ci95: `${lo}-${hi}%`, medianOkS: median(c.okTimes), iqrS: [quart(c.okTimes, 0.25), quart(c.okTimes, 0.75)], recorded: c.recN ? `${c.rec}/${c.recN}` : "n/a", costUsd: +c.cost.toFixed(2) };
});

if (process.argv.includes("--md")) {
  console.log("| Task | Environment | As scored | Adjusted | 95% CI | Median time (passes) | Recorded | Cost |\n|---|---|---|---|---|---|---|---|");
  for (const r of rows) console.log(`| ${r.task} | ${r.env} | ${r.asScored} | ${r.adjusted} | ${r.ci95} | ${r.medianOkS === null ? "n/a" : Math.round(r.medianOkS) + " s"} | ${r.recorded} | $${r.costUsd} |`);
} else console.log(JSON.stringify(rows, null, 1));
console.log(`\ncompleted ${done.length}, infrastructure excluded ${infra.length}${infra.length ? ": " + infra.map((r) => `${r.id.slice(0, 8)} (${r.metadata?.failureDetails?.kind ?? r.status})`).join(", ") : ""}, adjustments ${adjust.length}`);
