import { useEffect, useState } from "react";

import AppLayout from "./components/layout/AppLayout";
import EventsPanel from "./features/events/EventsPanel";
import MapSection from "./features/events/MapSection";
import CountryPanel from "./features/events/CountryPanel";
import type { HeatmapCountry } from "./types/heatmap";


export default function App() {
  const [selectedEvent, setSelectedEvent] = useState(null);
  const [heatmapData, setHeatmapData] =
  useState<HeatmapCountry[]>([]);
  const [selectedCountry, setSelectedCountry] = useState<any>(null);

  const [countryStatements, setCountryStatements] = useState<any[]>([]);

  // RESET dependent state when event changes
  useEffect(() => {
    setSelectedCountry(null);
    setCountryStatements([]);
  }, [selectedEvent]);


  return (
    <AppLayout>
      <EventsPanel
        selectedEvent={selectedEvent}
        setSelectedEvent={setSelectedEvent}
        setHeatmapData={setHeatmapData}
      />
      <MapSection
        heatmapData={heatmapData}
        selectedEvent={selectedEvent}
        setSelectedCountry={setSelectedCountry}
        setCountryStatements={setCountryStatements}
      />
      <CountryPanel
        selectedCountry={selectedCountry}
        countryStatements={countryStatements}
        selectedEvent={selectedEvent}
      />
    </AppLayout>
  );
}
