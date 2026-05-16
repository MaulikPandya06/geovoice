import { useState, useEffect } from "react";
import OverviewTab from "../../components/common/OverviewTab";
import StatementsTab from "../../components/common/StatementsTab";
import InsightsTab from "../../components/common/InsightsTab";
import { getInvolvement } from "../../utils/involvement";
import { fetchWithLoading } from "../../services/fetchWithLoading";

type Props = {
  selectedCountry: any;
  countryStatements: any[];
  selectedEvent: any;
};

type TabButtonProps = {
  active: boolean;
  onClick: () => void;
  children: React.ReactNode;
};

function TabButton({
  active,
  onClick,
  children,
}: TabButtonProps) {
  return (
    <button
      onClick={onClick}
      className={`
        relative
        pb-2
        text-[13px]
        font-medium
        transition

        ${
          active
            ? "text-blue-400"
            : "text-gray-400 hover:text-white"
        }
      `}
    >
      {children}

      {active && (
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
      )}
    </button>
  );
}


export default function CountryPanel({
  selectedCountry,
  countryStatements,
  selectedEvent,
}: Props) {

  const [activeTab, setActiveTab] =
  useState<"overview" | "statements" | "insights">(
    "overview"
  );

  const [summary, setSummary] = useState("");
  const [summaryLoading, setSummaryLoading] = useState(false);
  const [summaryError, setSummaryError] = useState("");

  const statementCount = countryStatements.length;

  const involvementData =
  getInvolvement(statementCount);

  const fetchSummary = async () => {
    if (!selectedCountry || !selectedEvent) return;

    try {
      setSummaryLoading(true);
      setSummaryError("");

      const params = new URLSearchParams({
        country: selectedCountry.country_name,
        event: selectedEvent.title,
      });

      const API_URL = import.meta.env.VITE_API_URL;
      // const response = await fetch(`${API_URL}/api/summary/?${params.toString()}`, {
      const response = await fetchWithLoading(`${API_URL}/api/summary/?${params.toString()}`, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || "Failed to fetch summary");
      }

      setSummary(data.summary);
    } catch (err: any) {
        setSummaryError(err.message);
    } finally {
        setSummaryLoading(false);
    }
  };


  useEffect(() => {
    fetchSummary();
  }, [selectedCountry, selectedEvent]);



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
          <div className="flex items-start justify-between gap-3">
            {/* Country */}
            <div className="flex min-w-0 items-start gap-2.5">

              {/* Flag */}
              <div
                className="
                  h-10 w-[58px]
                  overflow-hidden
                  rounded-lg
                  border border-gray-700/60
                  shrink-0
                "
              >
                <img
                  src={`https://flagcdn.com/w320/${selectedCountry?.isoa2_code?.toLowerCase()}.png`}
                  alt={`${selectedCountry?.full_name} Flag`}
                  className="h-full w-full object-cover"
                />
              </div>

              {/* Name */}
              <div className="min-w-0 pt-0.5">
                <h2
                  className="
                    truncate
                    text-[17px]
                    font-semibold
                    leading-5
                    tracking-tight
                    text-white
                  "
                >
                  {selectedCountry?.country_name || "Select Country"}
                </h2>

                <p className="mt-0.5 truncate text-[12px] leading-4 text-gray-400">
                  {selectedCountry?.full_name}
                </p>
              </div>
            </div>

          </div>

        {/* Stats */}
        <div className="mt-4 flex items-center justify-between gap-4">

          {/* Left */}
          <div className="min-w-0 flex-1">

            <p className="text-[12px] font-medium text-gray-400">
              Involvement Level
            </p>

            <div className="mt-1.5 flex items-center gap-1.5">
              <div
                className={`h-1.5 w-1.5 rounded-full ${involvementData.dotColor}`}
              />

              <span
                className={`text-[15px] font-semibold leading-none ${involvementData.textColor}`}
              >
                {involvementData.label}
              </span>
            </div>

            {/* Bars */}
            <div className="mt-3 flex gap-1.5">
              {[1, 2, 3, 4, 5].map((i) => (
                <div
                  key={i}
                  className={`
                    h-2
                    flex-1
                    rounded-full
                    transition-all

                    ${
                      i <= involvementData.activeBars
                        ? "bg-gradient-to-r from-red-500 via-orange-400 to-orange-300"
                        : "bg-gray-800"
                    }
                  `}
                />
              ))}
            </div>
          </div>

          {/* Circle */}
          <div className="relative h-20 w-20 shrink-0">

            {/* Glow */}
            <div
              className="
                absolute inset-0
                rounded-full
                bg-red-500/10
                blur-lg
              "
            />

            {/* Ring */}
            <div
              className="
                absolute inset-0
                rounded-full
                border-[3px]
                border-orange-400
                border-r-red-500
                border-b-red-600
              "
            />

            {/* Inner */}
            <div
              className="
                absolute inset-[7px]
                flex flex-col
                items-center
                justify-center
                rounded-full
                border border-gray-800
                bg-[#07111f]
              "
            >
              <span className="text-2xl font-bold leading-none text-white">
                {countryStatements.length}
              </span>

              <span className="mt-0.5 text-[10px] text-gray-400">
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
          <TabButton
            active={activeTab === "overview"}
            onClick={() => setActiveTab("overview")}
          >
            Overview
          </TabButton>

          <TabButton
            active={activeTab === "statements"}
            onClick={() => setActiveTab("statements")}
          >
            Statements ({countryStatements.length})
          </TabButton>

          <TabButton
            active={activeTab === "insights"}
            onClick={() => setActiveTab("insights")}
          >
            AI Insights
          </TabButton>
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
        {activeTab === "overview" && (
          <OverviewTab
            // selectedEvent={selectedEvent}
            countryStatements={countryStatements}
            summaryLoading={summaryLoading}
            summaryError={summaryError}
            summary={summary}

          />
        )}

        {/* Statements */}
        {activeTab === "statements" && (
          <StatementsTab
            countryStatements={countryStatements}
            // selectedCountry={selectedCountry}
          />
        )}

        {/* AI Summary */}
        {activeTab === "insights" && (
          <InsightsTab
            selectedEvent={selectedEvent}
            selectedCountry={selectedCountry}
          />
        )}

        {/* Distribution */}
        {/* <section
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
          </h3> */}

          {/* Chart */}
          {/* <div className="mt-6 h-36 flex items-end gap-[4px]">
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
          </div> */}

          {/* Timeline */}
          {/* <div className="mt-3 flex justify-between text-[11px] text-gray-500">
            <span>Oct 2023</span>
            <span>Dec 2023</span>
            <span>Feb 2024</span>
            <span>Apr 2024</span>
            <span>May 2024</span>
          </div> */}
        {/* </section> */}

        {/* CTA */}
        {/* <button
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
          ◈ View All Statements (23)
          ◈ View All Statements ({countryStatements.length})
        </button>  */}
      </div>
    </aside>
  );
}