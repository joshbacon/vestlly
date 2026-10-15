// Fields considered "static" metadata
const META_FIELDS = [
  'longName', 'symbol', 'sector', 'industry',
  'currency', 'exchange', 'website',
];

export function reshapeByTicker(flatRecords) {
  const byTicker = new Map();

  for (const record of flatRecords) {
    const { symbol, date, ...rest } = record;
    if (symbol == null) continue;

    if (!byTicker.has(symbol)) {
      byTicker.set(symbol, { symbol, meta: {}, history: [] });
    }
    const entry = byTicker.get(symbol);

    // pull out meta fields, keep everything else as the date's data point
    const meta = {};
    const dynamic = { date };
    for (const [key, value] of Object.entries(rest)) {
      if (META_FIELDS.includes(key)) {
        meta[key] = value;
      } else {
        dynamic[key] = value;
      }
    }

    // meta gets overwritten each time — effectively "most recent wins"
    // since files are processed in whatever order they were read; sort first if you want "earliest wins" instead
    Object.assign(entry.meta, meta);
    entry.history.push(dynamic);
  }

  // sort each ticker's history chronologically
  for (const entry of byTicker.values()) {
    entry.history.sort((a, b) => a.date.localeCompare(b.date));
  }

  return Array.from(byTicker.values());
}