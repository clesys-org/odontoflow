"use client";

import type { Tooth } from "@/lib/types/clinical";

/* ---- Color mappings ---- */

const SURFACE_COLORS: Record<string, string> = {
  HEALTHY: "#22c55e",
  CARIES: "#ef4444",
  RESTORATION: "#3b82f6",
  FRACTURE: "#f59e0b",
  SEALANT: "#8b5cf6",
  CROWN: "#6b7280",
  VENEER: "#06b6d4",
};

const SURFACE_LABELS: Record<string, string> = {
  HEALTHY: "Saudavel",
  CARIES: "Carie",
  RESTORATION: "Restauracao",
  FRACTURE: "Fratura",
  SEALANT: "Selante",
  CROWN: "Coroa",
  VENEER: "Faceta",
};

/* ---- Tooth layout ---- */

const UPPER_RIGHT = [18, 17, 16, 15, 14, 13, 12, 11];
const UPPER_LEFT = [21, 22, 23, 24, 25, 26, 27, 28];
const LOWER_RIGHT = [48, 47, 46, 45, 44, 43, 42, 41];
const LOWER_LEFT = [31, 32, 33, 34, 35, 36, 37, 38];

const TOOTH_SIZE = 40;
const GAP = 4;
const QUADRANT_GAP = 14;

interface OdontogramSVGProps {
  teeth: Tooth[];
  onToothClick: (toothNumber: number) => void;
  selectedTooth: number | null;
}

function getSurfaceColor(tooth: Tooth, position: string): string {
  const surface = tooth.surfaces.find((s) => s.position === position);
  return surface ? SURFACE_COLORS[surface.condition] || "#22c55e" : "#22c55e";
}

function ToothGraphic({
  tooth,
  x,
  y,
  selected,
  onClick,
}: {
  tooth: Tooth | undefined;
  x: number;
  y: number;
  selected: boolean;
  onClick: () => void;
  toothNumber: number;
}) {
  const S = TOOTH_SIZE;
  const inset = S * 0.25; // inner square offset

  if (!tooth || tooth.status === "ABSENT") {
    return (
      <g onClick={onClick} className="cursor-pointer">
        <rect
          x={x}
          y={y}
          width={S}
          height={S}
          fill="none"
          stroke="#d1d5db"
          strokeWidth={1.5}
          strokeDasharray="4 3"
          rx={3}
        />
        {tooth?.status === "ABSENT" && (
          <>
            <line x1={x + 4} y1={y + 4} x2={x + S - 4} y2={y + S - 4} stroke="#d1d5db" strokeWidth={1.5} />
            <line x1={x + S - 4} y1={y + 4} x2={x + 4} y2={y + S - 4} stroke="#d1d5db" strokeWidth={1.5} />
          </>
        )}
      </g>
    );
  }

  const isImplant = tooth.status === "IMPLANT";
  const isRootRemnant = tooth.status === "ROOT_REMNANT";

  // Surface colors
  const vestibularColor = getSurfaceColor(tooth, "VESTIBULAR");
  const lingualColor = getSurfaceColor(tooth, "LINGUAL");
  const mesialColor = getSurfaceColor(tooth, "MESIAL");
  const distalColor = getSurfaceColor(tooth, "DISTAL");
  const oclusalColor = getSurfaceColor(tooth, "OCLUSAL");

  return (
    <g onClick={onClick} className="cursor-pointer">
      {/* Selection highlight */}
      {selected && (
        <rect
          x={x - 3}
          y={y - 3}
          width={S + 6}
          height={S + 6}
          fill="none"
          stroke="#14b8a6"
          strokeWidth={2.5}
          rx={5}
        />
      )}

      {/* Vestibular (top trapezoid) */}
      <polygon
        points={`${x},${y} ${x + S},${y} ${x + S - inset},${y + inset} ${x + inset},${y + inset}`}
        fill={isImplant ? "#94a3b8" : vestibularColor}
        stroke="#fff"
        strokeWidth={1}
      />

      {/* Lingual (bottom trapezoid) */}
      <polygon
        points={`${x + inset},${y + S - inset} ${x + S - inset},${y + S - inset} ${x + S},${y + S} ${x},${y + S}`}
        fill={isImplant ? "#94a3b8" : lingualColor}
        stroke="#fff"
        strokeWidth={1}
      />

      {/* Mesial (left trapezoid) */}
      <polygon
        points={`${x},${y} ${x + inset},${y + inset} ${x + inset},${y + S - inset} ${x},${y + S}`}
        fill={isImplant ? "#94a3b8" : mesialColor}
        stroke="#fff"
        strokeWidth={1}
      />

      {/* Distal (right trapezoid) */}
      <polygon
        points={`${x + S},${y} ${x + S},${y + S} ${x + S - inset},${y + S - inset} ${x + S - inset},${y + inset}`}
        fill={isImplant ? "#94a3b8" : distalColor}
        stroke="#fff"
        strokeWidth={1}
      />

      {/* Oclusal (center square) */}
      <rect
        x={x + inset}
        y={y + inset}
        width={S - 2 * inset}
        height={S - 2 * inset}
        fill={isImplant ? "#64748b" : oclusalColor}
        stroke="#fff"
        strokeWidth={1}
      />

      {/* Border */}
      <rect
        x={x}
        y={y}
        width={S}
        height={S}
        fill="none"
        stroke={isRootRemnant ? "#92400e" : "#374151"}
        strokeWidth={isRootRemnant ? 2 : 1}
        rx={2}
      />

      {/* Implant label */}
      {isImplant && (
        <text
          x={x + S / 2}
          y={y + S / 2 + 1}
          textAnchor="middle"
          dominantBaseline="middle"
          fill="#fff"
          fontSize={14}
          fontWeight="bold"
        >
          I
        </text>
      )}
    </g>
  );
}

export default function OdontogramSVG({
  teeth,
  onToothClick,
  selectedTooth,
}: OdontogramSVGProps) {
  const teethMap = new Map(teeth.map((t) => [t.tooth_number, t]));

  function renderQuadrant(
    numbers: number[],
    startX: number,
    y: number
  ) {
    return numbers.map((num, i) => {
      const x = startX + i * (TOOTH_SIZE + GAP);
      const tooth = teethMap.get(num);
      return (
        <g key={num}>
          <ToothGraphic
            tooth={tooth}
            toothNumber={num}
            x={x}
            y={y}
            selected={selectedTooth === num}
            onClick={() => onToothClick(num)}
          />
          {/* Tooth number label */}
          <text
            x={x + TOOTH_SIZE / 2}
            y={y + TOOTH_SIZE + 14}
            textAnchor="middle"
            fill={selectedTooth === num ? "#0d9488" : "#6b7280"}
            fontSize={11}
            fontWeight={selectedTooth === num ? "bold" : "normal"}
          >
            {num}
          </text>
        </g>
      );
    });
  }

  const quadrantWidth = 8 * (TOOTH_SIZE + GAP) - GAP;
  const totalWidth = 2 * quadrantWidth + QUADRANT_GAP + 40; // padding
  const paddingX = 20;
  const upperY = 20;
  const labelHeight = 20;
  const archGap = 30;
  const lowerY = upperY + TOOTH_SIZE + labelHeight + archGap;
  const totalHeight = lowerY + TOOTH_SIZE + labelHeight + 20;

  const upperRightX = paddingX;
  const upperLeftX = paddingX + quadrantWidth + QUADRANT_GAP;
  const lowerRightX = paddingX;
  const lowerLeftX = paddingX + quadrantWidth + QUADRANT_GAP;

  return (
    <div className="space-y-4">
      <svg
        viewBox={`0 0 ${totalWidth} ${totalHeight}`}
        className="w-full max-w-[860px] mx-auto"
        style={{ minHeight: 260 }}
      >
        {/* Center dividing line */}
        <line
          x1={paddingX + quadrantWidth + QUADRANT_GAP / 2}
          y1={upperY - 5}
          x2={paddingX + quadrantWidth + QUADRANT_GAP / 2}
          y2={lowerY + TOOTH_SIZE + labelHeight + 5}
          stroke="#d1d5db"
          strokeWidth={1}
          strokeDasharray="6 4"
        />

        {/* Horizontal divider between arches */}
        <line
          x1={paddingX - 5}
          y1={upperY + TOOTH_SIZE + labelHeight + archGap / 2}
          x2={totalWidth - paddingX + 5}
          y2={upperY + TOOTH_SIZE + labelHeight + archGap / 2}
          stroke="#d1d5db"
          strokeWidth={1}
          strokeDasharray="6 4"
        />

        {/* Arch labels */}
        <text x={paddingX} y={upperY - 5} fill="#9ca3af" fontSize={10} fontWeight="500">
          Superior
        </text>
        <text x={paddingX} y={lowerY - 5} fill="#9ca3af" fontSize={10} fontWeight="500">
          Inferior
        </text>

        {/* Upper arch */}
        {renderQuadrant(UPPER_RIGHT, upperRightX, upperY)}
        {renderQuadrant(UPPER_LEFT, upperLeftX, upperY)}

        {/* Lower arch */}
        {renderQuadrant(LOWER_RIGHT, lowerRightX, lowerY)}
        {renderQuadrant(LOWER_LEFT, lowerLeftX, lowerY)}
      </svg>

      {/* Legend */}
      <div className="flex flex-wrap gap-3 justify-center text-xs">
        {Object.entries(SURFACE_COLORS).map(([key, color]) => (
          <div key={key} className="flex items-center gap-1.5">
            <span
              className="w-3 h-3 rounded-sm inline-block border border-gray-200"
              style={{ backgroundColor: color }}
            />
            <span className="text-gray-600">{SURFACE_LABELS[key]}</span>
          </div>
        ))}
        <div className="flex items-center gap-1.5">
          <span className="w-3 h-3 rounded-sm inline-block border border-gray-300 border-dashed" />
          <span className="text-gray-600">Ausente</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-3 h-3 rounded-sm inline-block bg-slate-500 text-white text-[8px] flex items-center justify-center font-bold leading-none">I</span>
          <span className="text-gray-600">Implante</span>
        </div>
      </div>
    </div>
  );
}
