// import { useGlobalStore } from "../../store/useGlobalStore";
import { useEffect, useState } from "react";
import type { HeatmapCountry } from "../../types/heatmap";


// const events = [
//   { id: 1, title: "Israel-Hamas War" },
//   { id: 2, title: "Russia-Ukraine Conflict" },
// ];

type EventType = {
  id: number;
  title: string;
  description: string;
  start_date: string;
  end_date: string | null;
};

type Props = {
  selectedEvent: any;
  setSelectedEvent: (event: any) => void;
  setHeatmapData: React.Dispatch<
  React.SetStateAction<HeatmapCountry[]>
>;
};

export default function EventsPanel({
  selectedEvent,
  setSelectedEvent,
  setHeatmapData,
}: Props) {
  // const { selectedEvent, setEvent } = useGlobalStore();

  const [events, setEvents] = useState<EventType[]>([]);
  const API_URL = import.meta.env.VITE_API_URL;

  useEffect(() => {
    const fetchEvents = async () => {
      try {
        const res = await fetch(
          `${API_URL}/api/events/`
        );

        const data = await res.json();

        setEvents(data);

        // 🔥 Auto-select first event
        if (data.length > 0) {
          handleEventClick(data[0]);
        }
      } catch (err) {
        console.error(err);
      }
    };

    fetchEvents();
  }, []);

  const handleEventClick = async (event: any) => {
  setSelectedEvent(event);
  const API_URL = import.meta.env.VITE_API_URL;

  try {
    const res = await fetch(
      `${API_URL}/api/events/${event.id}/heatmap/`
    );

    const data = await res.json();

    setHeatmapData(data);
    } catch (err) {
      console.error(err);
    }
  };



  return (
  <aside
    className="
      w-full
      sm:w-[320px]
      lg:w-[340px]
      shrink-0
      border-r border-gray-800
      bg-gray-950
      flex flex-col
      min-h-0
    "
  >
    {/* Header */}
    <div className="px-5 py-4 border-b border-gray-800 shrink-0">
      <h2 className="text-lg font-semibold text-white tracking-tight">
        Global Events
      </h2>

      {/* <p className="text-xs text-gray-400 mt-1">
        Active geopolitical conflicts & developments
      </p> */}
    </div>

    {/* Events List */}
    <div className="flex-1 overflow-y-auto p-4 space-y-3">
      {events.map((event) => {
        const isSelected = selectedEvent?.id === event.id;

        return (
          <button
            key={event.id}
            onClick={() => handleEventClick(event)}
            className={`
              group
              w-full
              rounded-2xl
              border
              p-4
              text-left
              transition-all
              duration-200
              backdrop-blur-sm
              hover:-translate-y-[1px]
              ${
                isSelected
                  ? "border-blue-500/40 bg-blue-500/10 shadow-lg shadow-blue-500/10"
                  : "border-gray-800 bg-gray-900/70 hover:border-gray-700 hover:bg-gray-900"
              }
            `}
          >
            {/* Event Title */}
            <div className="flex items-start justify-between gap-3">
              <h3
                className={`
                  text-sm sm:text-[15px]
                  font-semibold
                  leading-snug
                  transition-colors
                  ${
                    isSelected
                      ? "text-blue-100"
                      : "text-gray-100 group-hover:text-white"
                  }
                `}
              >
                {event.title}
              </h3>

              {/* Status Badge */}
              <span
                className={`
                  shrink-0
                  rounded-full
                  px-2 py-1
                  text-[10px]
                  font-medium
                  uppercase
                  tracking-wide
                  ${
                    event.end_date
                      ? "bg-gray-800 text-gray-300"
                      : "bg-emerald-500/15 text-emerald-400 border border-emerald-500/20"
                  }
                `}
              >
                {event.end_date ? "Ended" : "Ongoing"}
              </span>
            </div>

            {/* Dates */}
            <div className="mt-3 flex items-center gap-2 text-xs sm:text-sm text-gray-400">
              <span>
                {new Date(event.start_date).toLocaleDateString()}
              </span>

              <span className="text-gray-600">•</span>

              <span>
                {event.end_date
                  ? new Date(event.end_date).toLocaleDateString()
                  : "Present"}
              </span>
            </div>
          </button>
        );
      })}
    </div>

    {/* Footer Note */}
    <div className="shrink-0 border-t border-gray-800 p-4">
      <div
        className="
          flex items-start gap-3
          rounded-2xl
          border border-blue-500/20
          bg-blue-500/10
          px-4
          py-3
          backdrop-blur-sm
        "
      >
        {/* Info Icon */}
        <div
          className="
            mt-0.5
            flex h-5 w-5 shrink-0 items-center justify-center
            rounded-full
            bg-blue-500/20
            text-[11px]
            font-bold
            text-blue-300
          "
        >
          i
        </div>

        {/* Text */}
        <div>
          <p className="text-xs font-medium tracking-wide text-blue-200">
            Info
          </p>

          <p className="mt-1 text-xs leading-relaxed text-blue-100/80">
            More global events and geopolitical developments will be added soon.
          </p>
        </div>
      </div>
    </div>
  </aside>
);
}
