// returns sector count with industry breakdown

export function buildSectorBreakdown(marketData) {
  const sectorMap = new Map();

  for (const stock of marketData) {
    const sector = stock.meta.sector || 'Unknown';
    const industry = stock.meta.industry || 'Unknown';

    if (!sectorMap.has(sector)) {
      sectorMap.set(sector, { name: sector, count: 0, industries: new Map() });
    }

    const sectorEntry = sectorMap.get(sector);
    sectorEntry.count += 1;
    sectorEntry.industries.set(industry, (sectorEntry.industries.get(industry) || 0) + 1);
  }

  // convert to array shape recharts expects, with industries as a sorted array too
  return Array.from(sectorMap.values()).map((entry) => ({
    name: entry.name,
    value: entry.count,
    industries: Array.from(entry.industries.entries())
      .map(([industry, count]) => ({ industry, count }))
      .sort((a, b) => b.count - a.count),
  }));
}