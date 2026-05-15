import { formatDate } from "../../utils/formatDate";

type Props = {
  countryStatements: any[];
  selectedCountry: any;
};

export default function StatementsTab({
  countryStatements,
  selectedCountry,
}: Props) {

  return (
    <div className="relative pl-10">
        {/* Global timeline line */}
        <div
        className="
            absolute
            left-[15px]
            top-2
            bottom-2
            w-px
            bg-blue-500/20
        "
        />

        {/* Timeline items */}
        <div className="space-y-6">
        {countryStatements.map((statement, index) => (
            <div
            key={index}
            className="relative"
            >
            {/* Timeline dot */}
            <div
                className="
                absolute
                left-[-34px]
                top-2
                h-4
                w-4
                rounded-full
                border-[3px]
                border-blue-500
                bg-[#030712]
                z-10
                "
            />

            {/* Card */}
            <div
                className="
                rounded-2xl
                border border-gray-800/70
                bg-gradient-to-b
                from-[#08111f]
                to-[#050c18]
                p-4
                "
            >
                {/* Header */}
                <div className="flex items-start justify-between gap-3">
                <div className="min-w-0">
                    <h3 className="text-sm font-semibold text-white">
                    {formatDate(statement?.publish_date)}
                    </h3>

                    <p
                    className="
                        mt-1
                        text-xs
                        text-gray-400
                        line-clamp-1
                    "
                    >
                    {statement?.title}
                    </p>
                </div>
                </div>

                {/* Statement */}
                <p
                className="
                    mt-4
                    text-sm
                    leading-8
                    text-gray-200
                    line-clamp-5
                "
                >
                “{statement?.text}”
                </p>

                {/* Footer */}
                <div className="mt-5 flex items-center justify-between gap-3">
                <a
                    href={statement?.source_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="
                    rounded-full
                    bg-blue-500/10
                    px-3 py-1
                    text-[11px]
                    font-medium
                    text-blue-400
                    "
                >
                    Official Statement
                </a>

                <a
                    href={statement?.source_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="
                    text-sm
                    text-blue-400
                    hover:text-blue-300
                    transition-colors
                    duration-200
                    "
                >
                    ↗
                </a>
                </div>
            </div>
            </div>
        ))}
        </div>
    </div>
);;
}
