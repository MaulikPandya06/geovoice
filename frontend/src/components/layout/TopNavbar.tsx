export default function TopNavbar() {
  return (
    <header className="flex min-h-20 items-center justify-between">

      {/* Logo + Brand */}
      <div className="flex items-center gap-3">
        <img
          src="/logo.svg" // put your logo inside public/logo.png
          alt="GeoStance Logo"
          className="h-20 w-20 object-contain"
        />

        <h1 className="text-[29px] font-semibold tracking-tight text-white">
          Geo<span className="text-[#f97316]">Stance</span>
        </h1>
      </div>

    </header>
  );
}
