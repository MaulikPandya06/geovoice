import { useState } from "react";
import { X } from "lucide-react";

export default function DevelopmentBanner() {
  const [visible, setVisible] = useState(true);

  if (!visible) return null;

  return (
    <div
      className="
        relative
        z-50
        flex items-start gap-3

        border-b border-yellow-500/20
        bg-yellow-500/10

        px-4 py-3

        text-sm
        text-yellow-100
      "
    >
      {/* Content */}
      <div className="flex-1 pr-8">
        <span className="font-semibold">
          Development Notice:
        </span>{" "}
        Data and geopolitical insights shown may be incomplete or inaccurate
        as the platform is currently in active
        development.
      </div>

      {/* Close */}
      <button
        onClick={() => setVisible(false)}
        className="
          absolute
          right-3
          top-3

          rounded-md
          p-1

          text-yellow-200/80
          transition-colors

          hover:bg-yellow-500/10
          hover:text-white
        "
      >
        <X size={16} />
      </button>
    </div>
  );
}
