import { colors } from "../../map/utils/colorScale";

type LegendItem = {
  color: string;
  label: string;
};

export const legendItems = [
  {
    color: colors[0],
    label: "No Statements",
  },
  {
    color: colors[1],
    label: "1–3 Statements",
  },
  {
    color: colors[2],
    label: "4–5 Statements",
  },
  {
    color: colors[3],
    label: "6+ Statements",
  },
];

export default function MapLegend() {
  return (
    <div
      className="
        absolute z-10

        bottom-3 right-3
        md:bottom-5 md:right-5
        lg:bottom-6 lg:right-6

        max-w-[160px] sm:max-w-[180px]

        bg-gray-900/80 backdrop-blur-md
        border border-gray-800
        rounded-lg shadow-lg

        p-2 sm:p-3

        text-[10px] sm:text-xs
        space-y-1.5 sm:space-y-2
      "
    >
      {legendItems.map((item) => (
        <LegendRow key={item.label} {...item} />
      ))}
    </div>
  );
}

function LegendRow({ color, label }: LegendItem) {
  return (
    <div className="flex items-center gap-2">
      <span
        className="w-2.5 h-2.5 sm:w-3 sm:h-3 rounded-sm shrink-0"
        style={{ backgroundColor: color }}
      />
      <span className="text-gray-300 leading-tight">
        {label}
      </span>
    </div>
  );
}
