import DevelopmentBanner from "../common/DevelopmentBanner";
import TopNavbar from "../layout/TopNavbar";
import LoadingScreen from "../common/LoadingScreen";


export default function AppLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <>
    <LoadingScreen />
    <div className="h-dvh flex bg-gray-950 text-white overflow-hidden">
      {/* Sidebar (optional for now) */}

      <div className="flex flex-1 flex-col min-w-0">
        {/* Navbar */}
        <header className="h-14 border-b border-gray-800 flex items-center px-4 shrink-0">
          <TopNavbar />
        </header>

        <DevelopmentBanner />

        {/* Main */}
        <main className="flex flex-1 min-h-0 overflow-hidden">
          {children}
        </main>
      </div>
    </div>
    </>
  );
}
