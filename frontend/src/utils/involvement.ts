export type InvolvementLevel =
  | "none"
  | "low"
  | "medium"
  | "high";

type InvolvementConfig = {
  level: InvolvementLevel;
  label: string;

  mapColor: string;

  textColor: string;
  dotColor: string;

  activeBars: number;
};

export function getInvolvement(
  count: number
): InvolvementConfig {

  // No statements
  if (count === 0) {
    return {
      level: "none",
      label: "None",

      mapColor: "#374151",

      textColor: "text-gray-400",
      dotColor: "bg-gray-500",

      activeBars: 0,
    };
  }

  // Low
  if (count <= 3) {
    return {
      level: "low",
      label: "Low",

      mapColor: "#fde047",

      textColor: "text-yellow-400",
      dotColor: "bg-yellow-400",

      activeBars: 1,
    };
  }

  // Medium
  if (count <= 5) {
    return {
      level: "medium",
      label: "Medium",

      mapColor: "#fb923c",

      textColor: "text-orange-400",
      dotColor: "bg-orange-400",

      activeBars: 3,
    };
  }

  // High
  return {
    level: "high",
    label: "High",

    mapColor: "#ef4444",

    textColor: "text-red-500",
    dotColor: "bg-red-500",

    activeBars: 5,
  };
}
