/**
 * BKS Performance Evaluator — cron daily 10:00 UTC (12:00 CET)
 *
 * Scoring formula per agent:
 *   resolution_rate  = resolved / calls                 (weight 0.4)
 *   satisfaction     = (positive - negative) / calls    (weight 0.3)
 *   speed_score      = 1 - clamp(avg_ms / 5000, 0, 1)  (weight 0.2)
 *   escalation_penalty = escalated / calls              (weight -0.1)
 *
 * Final score: 0–100. Below 60 → flagged.
 */

const AGENTS     = ['catalog', 'custom', 'support', 'tier', 'orchestrator'];
const THRESHOLD  = 60;

function clamp(v, min, max) { return Math.min(Math.max(v, min), max); }

function scoreAgent(m) {
  if (!m.calls) return { score: null, issue: 'no_data' };

  const resolution    = m.resolved   / m.calls;
  const satisfaction  = clamp((m.positive - m.negative) / m.calls, -1, 1);
  const avgMs         = m.calls ? m.total_ms / m.calls : 0;
  const speed         = 1 - clamp(avgMs / 5000, 0, 1);
  const escalationPen = m.escalated / m.calls;

  const score = Math.round(
    (resolution  * 0.4 +
     ((satisfaction + 1) / 2) * 0.3 +
     speed * 0.2 -
     escalationPen * 0.1) * 100
  );

  const issues = [];
  if (resolution   < 0.6) issues.push(`bassa risoluzione (${(resolution * 100).toFixed(0)}%)`);
  if (m.negative   > m.positive) issues.push('sentiment negativo prevalente');
  if (avgMs        > 4000) issues.push(`risposta lenta (avg ${avgMs.toFixed(0)}ms)`);
  if (escalationPen > 0.3) issues.push(`alto tasso escalation (${(escalationPen * 100).toFixed(0)}%)`);

  return { score, issues, resolution, satisfaction, speed, calls: m.calls };
}

export async function runEvaluation(memory) {
  const report = {
    date:   new Date().toISOString(),
    agents: [],
    overall: 0,
    flags:  [],
  };

  let scoredCount = 0;
  let totalScore  = 0;

  for (const name of AGENTS) {
    const metrics = await memory.getMetrics(name);
    const { score, issues, ...stats } = scoreAgent(metrics);

    report.agents.push({ name, score, issues: issues ?? [], ...stats, raw: metrics });

    if (score !== null) {
      scoredCount++;
      totalScore += score;
      if (score < THRESHOLD) {
        report.flags.push({ agent: name, score, issues });
      }
    }
  }

  report.overall = scoredCount ? Math.round(totalScore / scoredCount) : null;
  await memory.saveEvalReport(report);
  return report;
}
