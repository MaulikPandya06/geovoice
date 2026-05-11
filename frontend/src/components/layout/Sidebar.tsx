import { Globe, LayoutDashboard, Brain } from "lucide-react";

const menu = [
  { label: "Dashboard", icon: LayoutDashboard },
  { label: "Global Map", icon: Globe },
  { label: "AI Insights", icon: Brain },
];

export default function Sidebar() {
  return (
    <aside className="hidden lg:flex w-64 flex-col border-r border-gray-800 bg-gray-900">
      <div className="p-4 text-xl font-bold">GeoVoice</div>

      <nav className="flex flex-col gap-2 px-2">
        {menu.map(({ label, icon: Icon }) => (
          <button
            key={label}
            className="flex items-center gap-3 rounded-lg px-3 py-2 hover:bg-gray-800 transition"
          >
            <Icon size={18} />
            {label}
          </button>
        ))}
      </nav>
    </aside>
  );
}
