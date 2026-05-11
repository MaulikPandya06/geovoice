import WorldMap from "../map/WorldMap";
import MapLegend from "../map/MapLegend";
import { useState } from "react";


type Props = {
  heatmapData: any[];
  selectedEvent: any;

  setSelectedCountry: (country: any) => void;

  setCountryStatements: (statements: any[]) => void;

};

export default function MapSection({
  heatmapData,
  selectedEvent,
  setSelectedCountry,
  setCountryStatements,
}: Props) {

  return (
    <section className="
      flex-1
      min-w-0
      min-h-0
      relative
    ">
      <WorldMap
        heatmapData={heatmapData}
        selectedEvent={selectedEvent}
        setSelectedCountry={setSelectedCountry}
        setCountryStatements={setCountryStatements}
        />
      <MapLegend />
    </section>
  );
}
