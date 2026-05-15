import { formatDate } from "../../utils/formatDate";


type Props = {
//   selectedEvent: any[];
  countryStatements: any[];
  summaryLoading: boolean;
  summaryError: string;
  summary: string;
};

export default function OverviewTab({
  countryStatements,
//   selectedEvent,
  summaryLoading,
  summaryError,
  summary

}: Props) {
    return(
        <div className="space-y-4">
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
                    {formatDate(countryStatements[0]?.publish_date)}
                    </span>
                </div>

                <p
                    className="
                    mt-4
                    text-sm
                    leading-7
                    text-gray-200
                    line-clamp-5
                    "
                >
                    {/* “Turkey continues to call for an immediate
                    cessation of hostilities and emphasizes the
                    importance of a two-state solution...” */}
                    “{countryStatements[0]?.text}”
                </p>

                <a
                    href={countryStatements[0]?.source_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="
                    inline-flex items-center gap-1
                    mt-4
                    text-sm font-medium
                    text-blue-400
                    transition-colors duration-200
                    hover:text-blue-300
                    "
                >
                    Original Statement ↗
                </a>
            </section>
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

                {/* <p
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
                </p> */}

                {summaryLoading ? (
                    <p className="text-gray-400 text-sm">
                    Generating AI summary...
                    </p>
                ) : summaryError ? (
                    <p className="text-red-400 text-sm">
                    {summaryError}
                    </p>
                ) : (
                    <p className="text-gray-300 leading-7 text-sm">
                    {summary}
                    </p>
                )}
            </section>
        </div>

    )
}