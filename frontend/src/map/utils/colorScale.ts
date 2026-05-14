import * as d3 from "d3";

export const thresholds = [1, 4, 6];

export const colors = [
  "#374151", // No statements
  "#fde047", // Low
  "#fb923c", // Medium
  "#ef4444", // High
];

export const colorScale = d3
  .scaleThreshold<number, string>()
  .domain(thresholds)
  .range(colors);

export default colorScale;
