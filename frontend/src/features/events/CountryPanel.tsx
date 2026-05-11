type Props = {
  selectedCountry: any;
  countryStatements: any[];
};


export default function CountryPanel({
  selectedCountry,
  countryStatements,
}: Props) {

  const statementCount = countryStatements.length;

  let involvement = "Low";
  let involvementColor = "text-yellow-400";
  let involvementDotColor = "bg-yellow-400";

  if (statementCount >= 20) {
    involvement = "High";
    involvementColor = "text-red-500";
    involvementDotColor = "bg-red-500";

  } else if (statementCount >= 10) {
    involvement = "Medium";
    involvementColor = "text-orange-400";
    involvementDotColor = "bg-orange-400";
  }
  const activeBars =
  involvement === "High"
    ? 5
    : involvement === "Medium"
    ? 3
    : 1;

  console.log("Selected Country:", selectedCountry);

  if (!selectedCountry) {
    return (
      <aside
        className="
          w-full
          sm:w-[360px]
          xl:w-[380px]
          shrink-0
          border-l border-gray-800/80
          bg-[#030712]
          flex items-center justify-center
          p-8
        "
      >
        <div className="text-center max-w-[260px]">
          {/* Icon */}
          <div
            className="
              mx-auto
              mb-5
              flex h-16 w-16
              items-center justify-center
              rounded-2xl
              border border-gray-800
              bg-gray-900/60
              text-3xl
            "
          >
            🌍
          </div>

          {/* Heading */}
          <h2 className="text-lg font-semibold text-white">
            No Country Selected
          </h2>

          {/* Description */}
          <p
            className="
              mt-3
              text-sm
              leading-6
              text-gray-400
            "
          >
            Select a country from the world map
            to view official statements,
            involvement level, and geopolitical
            insights related to the selected event.
          </p>
        </div>
      </aside>
    );
  }

  if (countryStatements.length === 0) {
    return (
      <aside
        className="
          w-full
          sm:w-[360px]
          xl:w-[380px]
          shrink-0
          border-l border-gray-800/80
          bg-[#030712]
          flex flex-col
        "
      >
        {/* Header */}
        <div className="p-4 border-b border-gray-800">
          <div className="flex items-start gap-3">
            {/* Flag */}
            <div
              className="
                h-12 w-[70px]
                overflow-hidden
                rounded-xl
                border border-gray-700/70
                shrink-0
              "
            >
              <img
                src={`https://flagcdn.com/w320/${selectedCountry?.isoa2_code?.toLowerCase()}.png`}
                alt={selectedCountry?.country_name}
                className="h-full w-full object-cover"
              />
            </div>

            {/* Name */}
            <div>
              <h2 className="text-xl font-semibold text-white">
                {selectedCountry?.country_name}
              </h2>

              <p className="text-sm text-gray-400 mt-1">
                {selectedCountry?.full_name}
              </p>
            </div>
          </div>
        </div>

        {/* Empty State */}
        <div
          className="
            flex-1
            flex
            items-center
            justify-center
            p-8
          "
        >
          <div className="text-center max-w-[260px]">
            <div className="text-4xl mb-4">
              📰
            </div>

            <h3 className="text-lg font-semibold text-white">
              No Statements Found
            </h3>

            <p className="mt-3 text-sm leading-6 text-gray-400">
              This country has not released any
              official statements related to the
              selected geopolitical event.
            </p>
          </div>
        </div>
      </aside>
    );
  }

  return (
    <aside
      className="
        w-full
        sm:w-[360px]
        xl:w-[380px]
        shrink-0
        border-l border-gray-800/80
        bg-[#030712]
        flex flex-col
        min-h-0
      "
    >
      {/* Header */}
      <div
        className="
          shrink-0
          border-b border-gray-800/80
          bg-gradient-to-b
          from-[#061120]
          to-[#030712]
          px-4
          pt-4
          pb-3
        "
      >
        {/* Top */}
        <div className="flex items-start justify-between gap-4">
          {/* Country */}
          <div className="flex items-start gap-3 min-w-0">
            {/* Flag */}
            <div
              className="
                h-12 w-[70px]
                overflow-hidden
                rounded-xl
                border border-gray-700/70
                shrink-0
              "
            >
              <img
                // src="https://flagcdn.com/w320/tr.png"
                src={`https://flagcdn.com/w320/${selectedCountry?.isoa2_code?.toLowerCase()}.png`}
                alt={`${selectedCountry?.full_name} Flag`}
                className="h-full w-full object-cover"
              />
            </div>

            {/* Name */}
            <div className="min-w-0">
              <h2
                className="
                  text-xl
                  font-semibold
                  tracking-tight
                  text-white
                  truncate
                "
              >
                {selectedCountry?.country_name || "Select Country"}
              </h2>

              <p className="mt-0.5 text-sm text-gray-400">
                {selectedCountry?.full_name}
              </p>
            </div>
          </div>

          {/* Close */}
          {/* <button
            className="
              rounded-lg
              p-2
              text-gray-500
              transition
              hover:bg-gray-800/70
              hover:text-white
            "
          >
            ✕
          </button> */}
        </div>

        {/* Stats */}
        <div className="mt-6 flex items-center justify-between gap-5">
          {/* Left */}
          <div className="flex-1 min-w-0">
            <p className="text-sm text-gray-400">
              Involvement Level
            </p>

            <div className="mt-2 flex items-center gap-2">
              <div className={`h-2 w-2 rounded-full ${involvementDotColor}`} />

              <span className={`text-lg font-semibold ${involvementColor}`}>
                {/* High */}
                {involvement}
              </span>
            </div>

            {/* Bars */}
            <div className="mt-4 flex gap-2">
              {[1, 2, 3, 4, 5].map((i) => (
                <div
                  key={i}
                  className={`
                    h-2.5
                    flex-1
                    rounded-full
                    transition-all

                    ${
                      i <= activeBars
                        ? "bg-gradient-to-r from-red-500 via-orange-400 to-orange-300"
                        : "bg-gray-800"
                    }
                  `}
                />
              ))}
            </div>
          </div>

          {/* Circle */}
          <div className="relative h-24 w-24 shrink-0">
            {/* Glow */}
            <div
              className="
                absolute inset-0
                rounded-full
                bg-red-500/10
                blur-xl
              "
            />

            {/* Ring */}
            <div
              className="
                absolute inset-0
                rounded-full
                border-[4px]
                border-orange-400
                border-r-red-500
                border-b-red-600
              "
            />

            {/* Inner */}
            <div
              className="
                absolute inset-[9px]
                rounded-full
                border border-gray-800
                bg-[#07111f]
                flex flex-col
                items-center
                justify-center
              "
            >
              <span className="text-3xl font-bold text-white leading-none">
                {/* 23 */}
                {countryStatements.length}
              </span>

              <span className="mt-1 text-[11px] text-gray-400">
                Statements
              </span>
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div
          className="
            mt-6
            flex items-center gap-5
            overflow-x-auto
            whitespace-nowrap

            [scrollbar-width:none]
            [-ms-overflow-style:none]
            [&::-webkit-scrollbar]:hidden
          "
        >
          {/* Active */}
          <button
            className="
              relative
              pb-2
              text-[13px]
              font-medium
              text-blue-400
            "
          >
            Overview

            <span
              className="
                absolute
                bottom-0
                left-0
                h-[2px]
                w-full
                rounded-full
                bg-blue-500
              "
            />
          </button>

          <button className="pb-2 text-[13px] text-gray-400 hover:text-white transition">
            {/* Statements (23) */}
            Statements ({countryStatements.length})
          </button>

          <button className="pb-2 text-[13px] text-gray-400 hover:text-white transition">
            Timeline
          </button>

          <button className="pb-2 text-[13px] text-gray-400 hover:text-white transition">
            Sources
          </button>
        </div>
      </div>

      {/* Content */}
      <div
        className="
          flex-1
          overflow-y-auto
          px-4
          py-4
          space-y-4

          [scrollbar-width:none]
          [-ms-overflow-style:none]
          [&::-webkit-scrollbar]:hidden
        "
      >
        {/* Latest Statement */}
        <section
          className="
            rounded-2xl
            border border-gray-800/70
            bg-gradient-to-b
            from-[#08111f]
            to-[#050c18]
            p-4
          "
        >
          <div className="flex items-center justify-between gap-4">
            <h3 className="text-base font-semibold text-white">
              Latest Statement
            </h3>

            <span className="text-xs text-gray-400">
              May 21, 2024
            </span>
          </div>

          <p
            className="
              mt-4
              text-sm
              leading-7
              text-gray-200
            "
          >
            {/* “Turkey continues to call for an immediate
            cessation of hostilities and emphasizes the
            importance of a two-state solution...” */}
            “{countryStatements[0]?.text}”
          </p>

          <button
            className="
              mt-4
              text-sm
              font-medium
              text-blue-400
              transition
              hover:text-blue-300
            "
          >
            Ministry of Foreign Affairs ↗
          </button>
        </section>

        {/* AI Summary */}
        <section
          className="
            rounded-2xl
            border border-gray-800/70
            bg-gradient-to-b
            from-[#08111f]
            to-[#050c18]
            p-4
          "
        >
          <div className="flex items-center gap-2">
            <h3 className="text-base font-semibold text-white">
              AI Summary
            </h3>

            <span
              className="
                rounded-md
                border border-gray-700
                bg-gray-800/80
                px-2 py-0.5
                text-[10px]
                font-semibold
                uppercase
                tracking-wide
                text-gray-300
              "
            >
              Beta
            </span>
          </div>

          <p
            className="
              mt-4
              text-sm
              leading-7
              text-gray-200
            "
          >
            Lorem Ipsum is simply dummy text of the printing and typesetting industry.
            Lorem Ipsum has been the industry's standard dummy text ever since the 1500s,
            into electronic typesetting, remaining essentially unchanged.
          </p>
        </section>

        {/* Distribution */}
        <section
          className="
            rounded-2xl
            border border-gray-800/70
            bg-gradient-to-b
            from-[#08111f]
            to-[#050c18]
            p-4
          "
        >
          <h3 className="text-base font-semibold text-white">
            Statement Distribution
          </h3>

          {/* Chart */}
          <div className="mt-6 h-36 flex items-end gap-[4px]">
            {[
              4, 5, 3, 6, 8, 4, 2, 3, 7, 9,
              5, 4, 2, 8, 4, 3, 5, 7, 4, 2,
              6, 8, 5, 4, 3, 7, 10, 12, 4,
            ].map((v, i) => (
              <div
                key={i}
                className="
                  flex-1
                  rounded-t-sm
                  bg-gradient-to-t
                  from-red-500
                  via-orange-400
                  to-orange-300
                "
                style={{
                  height: `${v * 6}px`,
                }}
              />
            ))}
          </div>

          {/* Timeline */}
          <div className="mt-3 flex justify-between text-[11px] text-gray-500">
            <span>Oct 2023</span>
            <span>Dec 2023</span>
            <span>Feb 2024</span>
            <span>Apr 2024</span>
            <span>May 2024</span>
          </div>
        </section>

        {/* CTA */}
        <button
          className="
            w-full
            rounded-2xl
            border border-blue-500/20
            bg-blue-500/10
            py-3
            text-sm
            font-medium
            text-blue-400
            transition-all
            hover:bg-blue-500/20
            hover:text-blue-300
          "
        >
          {/* ◈ View All Statements (23) */}
          ◈ View All Statements ({countryStatements.length})
        </button>
      </div>
    </aside>
  );
}