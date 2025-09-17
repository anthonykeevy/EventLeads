"use client";
// Shard refs: docs/shards/01-builder-ux.md (Canvas/canvas layouts, properties panel, snapping, preview guarantees)
import Link from "next/link";
import { useMemo, useState } from "react";

type DeviceKey =
  | "desktop-169"
  | "desktop-1610"
  | "desktop-43"
  | "tablet-portrait"
  | "tablet-landscape"
  | "mobile-portrait"
  | "mobile-landscape";

const DEVICES: Record<
  DeviceKey,
  { label: string; width: number; height: number }
> = {
  "desktop-169": { label: "Desktop 16:9 (1200×675)", width: 1200, height: 675 },
  "desktop-1610": { label: "Desktop 16:10 (1200×750)", width: 1200, height: 750 },
  "desktop-43": { label: "Desktop 4:3 (1024×768)", width: 1024, height: 768 },
  "tablet-portrait": { label: "Tablet Portrait (768×1024)", width: 768, height: 1024 },
  "tablet-landscape": { label: "Tablet Landscape (1024×768)", width: 1024, height: 768 },
  "mobile-portrait": { label: "Mobile Portrait (375×667)", width: 375, height: 667 },
  "mobile-landscape": { label: "Mobile Landscape (667×375)", width: 667, height: 375 },
};

function Sidebar() {
  return (
    <aside className="p-3 border-r border-neutral-800 bg-neutral-900 text-neutral-100 space-y-4">
      <div>
        <div className="text-sm font-semibold mb-2">Form Elements</div>
      </div>

      <div className="space-y-2">
        <div className="text-xs uppercase tracking-wide text-neutral-400">Background</div>
        <label className="block border border-dashed border-neutral-700 rounded p-4 text-center cursor-pointer hover:bg-neutral-800">
          <input type="file" className="hidden" />
          <span className="text-sm">Drop image here or click to upload</span>
        </label>
      </div>

      <div className="space-y-2">
        <div className="text-xs uppercase tracking-wide text-neutral-400">Form Fields</div>
        <div className="grid grid-cols-2 gap-2">
          {[
            "Text Input",
            "Email",
            "Phone",
            "Date",
            "Dropdown",
            "Text Area",
            "Checkbox",
            "Radio Button",
          ].map((label) => (
            <button
              key={label}
              className="text-left text-sm px-3 py-2 rounded border border-neutral-700 bg-neutral-800 hover:bg-neutral-700"
              type="button"
            >
              {label}
            </button>
          ))}
        </div>
      </div>
    </aside>
  );
}

function PropertiesPanel() {
  return (
    <aside className="p-3 border-l border-neutral-800 bg-neutral-900 text-neutral-100">
      <div className="text-sm font-semibold mb-2">Properties</div>
      <div className="text-neutral-400 text-sm">Select an element to edit properties</div>
    </aside>
  );
}

export default function BuilderShell({ eventId }: { eventId: string }) {
  const [device, setDevice] = useState<DeviceKey>("desktop-169");
  const [zoom, setZoom] = useState<number>(100);
  const [grid, setGrid] = useState<boolean>(false);
  const [snap, setSnap] = useState<boolean>(true);

  const dims = DEVICES[device];
  const zoomFactor = zoom / 100;

  const canvasStyle = useMemo(
    () => ({
      width: Math.round(dims.width * zoomFactor),
      height: Math.round(dims.height * zoomFactor),
    }),
    [dims.width, dims.height, zoomFactor]
  );

  return (
    <main className="h-screen grid grid-cols-[240px_1fr_320px] grid-rows-[auto_1fr] bg-neutral-950 text-neutral-100">
      <header className="col-span-3 flex items-center justify-between px-3 py-2 border-b border-neutral-800 bg-neutral-900">
        <div className="flex items-center gap-3">
          <div className="text-sm text-neutral-300">Target Device</div>
          <select
            className="bg-neutral-800 border border-neutral-700 rounded px-2 py-1 text-sm"
            value={device}
            onChange={(e) => setDevice(e.target.value as DeviceKey)}
          >
            {Object.entries(DEVICES).map(([key, obj]) => (
              <option key={key} value={key}>
                {obj.label}
              </option>
            ))}
          </select>
          <div className="text-sm text-neutral-400">
            Canvas: {dims.width} × {dims.height} &nbsp; Zoom: {zoom}%
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button
            className="px-2 py-1 rounded border border-neutral-700 bg-neutral-800 text-sm"
            onClick={() => setZoom((z) => Math.max(50, z - 10))}
          >
            -
          </button>
          <button
            className="px-2 py-1 rounded border border-neutral-700 bg-neutral-800 text-sm"
            onClick={() => setZoom((z) => Math.min(200, z + 10))}
          >
            +
          </button>
          <Link
            className="ml-2 px-3 py-1 rounded bg-emerald-600 hover:bg-emerald-500 text-white text-sm"
            href={`/preview/${eventId}`}
          >
            Preview
          </Link>
        </div>
      </header>

      <Sidebar />

      <section className="p-2 flex items-center justify-center bg-neutral-900">
        <div
          className="relative border border-neutral-700 bg-neutral-800 shadow-sm"
          style={canvasStyle}
        >
          {grid && (
            <div
              className="absolute inset-0 pointer-events-none"
              style={{
                backgroundImage:
                  "linear-gradient(to right, rgba(255,255,255,0.06) 1px, transparent 1px), linear-gradient(to bottom, rgba(255,255,255,0.06) 1px, transparent 1px)",
                backgroundSize: "8px 8px",
              }}
            />
          )}
          <div className="absolute top-2 left-2 flex items-center gap-3 text-xs text-neutral-300">
            <label className="inline-flex items-center gap-1">
              <input
                type="checkbox"
                className="accent-neutral-200"
                checked={grid}
                onChange={(e) => setGrid(e.target.checked)}
              />
              Grid
            </label>
            <label className="inline-flex items-center gap-1">
              <input
                type="checkbox"
                className="accent-neutral-200"
                checked={snap}
                onChange={(e) => setSnap(e.target.checked)}
              />
              Snap
            </label>
          </div>
        </div>
      </section>

      <PropertiesPanel />
    </main>
  );
}



