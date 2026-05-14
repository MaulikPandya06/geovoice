import { useEffect, useRef } from "react";
import * as d3 from "d3";
import { feature } from "topojson-client";
import worldData from "./world-110m.json";
import colorScale from "../../map/utils/colorScale";

type Props = {
  heatmapData: any[];
  selectedEvent: any;

  setSelectedCountry: (country: any) => void;

  setCountryStatements: (statements: any[]) => void;
};

export default function WorldMap({
  heatmapData,
  selectedEvent,
  setSelectedCountry,
  setCountryStatements,
}: Props) {
  const svgRef = useRef<SVGSVGElement | null>(null);

  useEffect(() => {
    if (!svgRef.current) return;

    const svg = d3.select(svgRef.current);

    const width = svgRef.current.clientWidth;
    const height = svgRef.current.clientHeight;

    svg.selectAll("*").remove();

    // 🌍 Geo data
    // const geo = feature(
    //   worldData as any,
    //   (worldData as any).objects.countries
    // );
    const objectKey =
      (worldData as any).objects.countries
        ? "countries"
        : "topo";

    const geo = feature(
      worldData as any,
      (worldData as any).objects[objectKey]
    );

    // 🌍 Projection
    // const projection = d3
    //   .geoNaturalEarth1()
    //   .scale(width / 6.5)
    //   .translate([width / 2, height / 2]);

    const projection = d3.geoNaturalEarth1().fitExtent(
      [
        [16, 16],
        [width - 16, height - 16],
      ],
      geo as any
    );

    const path = d3.geoPath(projection);


    // 🔥 Dummy data
    // const data: Record<string, number> = {
    //   USA: 12,
    //   IND: 18,
    //   RUS: 31,
    //   FRA: 24,
    //   BRA: 7,
    //   AUS: 5,
    //   SAU: 65,
    //   ZAF: 8,
    // };

    // 🎨 Color scale
    // const colorScale = d3
    //   .scaleThreshold<number, string>()
    //   .domain([1, 5, 20, 50])
    //   .range([
    //     "#374151",
    //     "#facc15",
    //     "#fb923c",
    //     "#f97316",
    //     "#dc2626",
    //   ]);

    // 🌍 Main group (for zoom)
    const g = svg.append("g");

    // 🧠 Tooltip div
    const tooltip = d3
      .select("body")
      .append("div")
      .style("position", "absolute")
      .style("background", "#111827")
      .style("padding", "6px 10px")
      .style("border-radius", "6px")
      .style("font-size", "12px")
      .style("color", "#fff")
      .style("pointer-events", "none")
      .style("opacity", 0);

    // 🌍 Draw countries
    g.selectAll("path")
      .data((geo as any).features)
      .join("path")
      .attr("d", path as any)
      // .attr("fill", (d: any) => {
      //   const countryId =
      //     d.id ||
      //     d.properties?.ISO_A3 ||
      //     d.properties?.ISO_A2;
      //   const value = data[countryId] || 0;
      //   return colorScale(value);
      // })
      .attr("fill", (d: any) => {
        const country = heatmapData.find(
          (c) => c.isoa3_code === d.properties.ISO_A3
        );

        const count = country?.statement_count || 0;

        return colorScale(count);
      })
      .attr("stroke", "#111827")
      .attr("stroke-width", 0.5)
      .style("cursor", "pointer")

      // On click, set selected country and fetch statements
      .on("click", async function (_, d: any) {
        const countryCode = d.properties?.ISO_A3;

        if (!countryCode || !selectedEvent) return;

        try {
          const res = await fetch(
            `http://127.0.0.1:8000/api/events/${selectedEvent.id}/countries/${countryCode}/statements/`
          );

          const data = await res.json();
          console.log("Country statements:", data);

          setCountryStatements(data.statements);

          if (data.country) {
            setSelectedCountry(data.country);
          }
        } catch (err) {
          console.error(err);
        }
      })

      // 🔥 Hover START
      .on("mouseover", function (event, d: any) {
        d3.select(this)
          .attr("stroke", "#fff")
          .attr("stroke-width", 1.5);

        const countryId =
          d.id ||
          d.properties?.ISO_A3 ||
          d.properties?.ISO_A2;

        // 🔥 Get real backend data
        const country = heatmapData.find(
          (c) => c.isoa3_code === countryId
        );

        const value = country?.statement_count || 0;

        // 🌍 Country name
        const countryName =
          d.properties?.name ||
          d.properties?.NAME ||
          "Unknown";

        tooltip
          .style("opacity", 1)
          .html(`
            <div style="font-weight:600">
              ${countryName}
            </div>

            <div style="
              font-size:11px;
              color:#9ca3af;
              margin-top:2px;
            ">
              ${value} statements
            </div>
          `);
      })

      .on("mousemove", function (event) {
        tooltip
          .style("left", event.pageX + 10 + "px")
          .style("top", event.pageY - 20 + "px");
      })

      .on("mouseout", function () {
        d3.select(this).attr("stroke", "#111827").attr("stroke-width", 0.5);

        tooltip.style("opacity", 0);
      });

    // 🔍 Zoom behavior
    const zoom = d3
      .zoom<SVGSVGElement, unknown>()
      .scaleExtent([1, 8])
      .on("zoom", (event) => {
        g.attr("transform", event.transform);
      });

    svg.call(zoom as any);

    // 🔘 Controls
    const zoomIn = () => {
      svg.transition().call(zoom.scaleBy as any, 1.3);
    };

    const zoomOut = () => {
      svg.transition().call(zoom.scaleBy as any, 0.7);
    };

    const reset = () => {
      svg
        .transition()
        .duration(500)
        .call(zoom.transform as any, d3.zoomIdentity);
    };

    // Attach to buttons
    document.getElementById("zoom-in")?.addEventListener("click", zoomIn);
    document.getElementById("zoom-out")?.addEventListener("click", zoomOut);
    document.getElementById("reset")?.addEventListener("click", reset);

    // Cleanup
    return () => {
      tooltip.remove();
    };
  }, [heatmapData]);

  return (
    <div className="w-full h-full relative">
      {/* Controls */}
      <div className="absolute top-4 left-4 z-10 flex flex-col gap-2">
        <button
          id="zoom-in"
          className="bg-gray-800 px-3 py-2 rounded hover:bg-gray-700"
        >
          +
        </button>

        <button
          id="zoom-out"
          className="bg-gray-800 px-3 py-2 rounded hover:bg-gray-700"
        >
          −
        </button>

        <button
          id="reset"
          className="bg-gray-800 px-3 py-2 rounded hover:bg-gray-700 text-xs"
        >
          Reset
        </button>
      </div>

      <svg
        ref={svgRef}
        className="w-full h-full block"
        preserveAspectRatio="xMidYMid meet"
      />
    </div>
  );
}