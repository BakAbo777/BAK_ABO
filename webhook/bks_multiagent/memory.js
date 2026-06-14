/**
 * BKS Long-Term Memory Layer — Cloudflare KV
 *
 * Schema:
 *   customer:{id}:profile   → { tier, preferences, interaction_count, last_seen }
 *   customer:{id}:history   → [{ role, content, agent, ts, resolved, sentiment }]
 *   agent:{name}:metrics    → { calls, resolved, escalated, positive, negative, total_ms }
 *   system:catalog_snapshot → { products, collections, updated_at }
 *   system:eval_report      → { date, agents: [{name, score, issues}] }
 */

const HISTORY_MAX = 40;
const TTL_PROFILE = 60 * 60 * 24 * 180;
const TTL_HISTORY = 60 * 60 * 24 * 90;
const TTL_METRICS = 60 * 60 * 24 * 365;

export class BKSMemory {
  constructor(kv) { this.kv = kv; }

  async getProfile(id) {
    return (await this.kv.get(`customer:${id}:profile`, 'json'))
      ?? { tier: 'none', preferences: {}, interaction_count: 0, last_seen: null };
  }

  async saveProfile(id, updates) {
    const cur = await this.getProfile(id);
    const p = { ...cur, ...updates, interaction_count: cur.interaction_count + 1, last_seen: new Date().toISOString() };
    await this.kv.put(`customer:${id}:profile`, JSON.stringify(p), { expirationTtl: TTL_PROFILE });
    return p;
  }

  async getHistory(id) {
    return (await this.kv.get(`customer:${id}:history`, 'json')) ?? [];
  }

  async appendHistory(id, turn) {
    const h = await this.getHistory(id);
    h.push({ ...turn, ts: new Date().toISOString() });
    await this.kv.put(`customer:${id}:history`, JSON.stringify(h.slice(-HISTORY_MAX)), { expirationTtl: TTL_HISTORY });
  }

  async getContextMessages(id, n = 10) {
    const h = await this.getHistory(id);
    return h.slice(-n).map(t => ({ role: t.role, content: t.content }));
  }

  async getMetrics(name) {
    return (await this.kv.get(`agent:${name}:metrics`, 'json'))
      ?? { calls: 0, resolved: 0, escalated: 0, positive: 0, negative: 0, total_ms: 0 };
  }

  async recordCall(name, { resolved, escalated, sentiment, ms }) {
    const m = await this.getMetrics(name);
    await this.kv.put(`agent:${name}:metrics`, JSON.stringify({
      calls:     m.calls + 1,
      resolved:  m.resolved  + (resolved  ? 1 : 0),
      escalated: m.escalated + (escalated ? 1 : 0),
      positive:  m.positive  + (sentiment === 'positive' ? 1 : 0),
      negative:  m.negative  + (sentiment === 'negative' ? 1 : 0),
      total_ms:  m.total_ms  + (ms || 0),
    }), { expirationTtl: TTL_METRICS });
  }

  async getCatalog() {
    return (await this.kv.get('system:catalog_snapshot', 'json')) ?? null;
  }

  async saveEvalReport(report) {
    await this.kv.put('system:eval_report', JSON.stringify(report), { expirationTtl: TTL_METRICS });
  }

  async getEvalReport() {
    return (await this.kv.get('system:eval_report', 'json')) ?? null;
  }
}
