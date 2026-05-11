import { Search } from "lucide-react";

export default function TopNavbar() {
  return (
    <header className="flex min-h-14 flex-wrap items-center gap-3 border-b border-gray-800 px-4 py-3 sm:flex-nowrap">
      <div className="min-w-0 flex-1 text-base font-medium">
        Global Event Monitor
      </div>

      <div className="flex h-10 w-full min-w-0 items-center gap-2 rounded-md bg-gray-900 px-3 sm:w-72">
        <Search size={16} className="shrink-0 text-gray-400" />
        <input
          className="min-w-0 flex-1 bg-transparent text-sm outline-none placeholder:text-gray-500"
          placeholder="Search events..."
        />
      </div>
    </header>
  );
}
