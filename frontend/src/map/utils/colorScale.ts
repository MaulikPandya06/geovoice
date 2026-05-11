import * as d3 from "d3";

export const thresholds = [1, 5, 20, 50];

export const colors = [
  "#374151", // no data
  "#facc15",
  "#fb923c",
  "#f97316",
  "#dc2626",
];

export const colorScale = d3
  .scaleThreshold<number, string>()
  .domain(thresholds)
  .range(colors);
