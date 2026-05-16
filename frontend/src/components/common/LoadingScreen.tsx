import { useGlobalStore } from "../../store/useGlobalStore";

export default function LoadingScreen() {
  const { isLoading } = useGlobalStore();

  if (!isLoading) return null;

  return (
    <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center z-50">
      <div className="w-[320px] max-w-full rounded-3xl border border-slate-800/90 bg-slate-900/95 p-8 shadow-[0_0_60px_rgba(15,23,42,0.5)]">
        <div className="mx-auto mb-5 h-14 w-14 rounded-full border-4 border-slate-700 border-t-sky-400 animate-spin" />
        <p className="text-center text-sm font-semibold uppercase tracking-[0.16em] text-slate-200">
          Loading, please wait...
        </p>
        <p className="mt-2 text-center text-xs text-slate-400">
          Fetching data from the server
        </p>
      </div>
    </div>
  );
}
