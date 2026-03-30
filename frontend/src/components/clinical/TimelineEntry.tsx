"use client";

import { useState } from "react";
import type { TimelineEntry as TimelineEntryType } from "@/lib/types/clinical";

const EVENT_ICONS: Record<string, { icon: React.ReactNode; bgColor: string }> = {
  note: {
    icon: (
      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
      </svg>
    ),
    bgColor: "bg-blue-100 text-blue-600",
  },
  appointment: {
    icon: (
      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
      </svg>
    ),
    bgColor: "bg-teal-100 text-teal-600",
  },
  prescription: {
    icon: (
      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
      </svg>
    ),
    bgColor: "bg-purple-100 text-purple-600",
  },
  payment: {
    icon: (
      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
      </svg>
    ),
    bgColor: "bg-green-100 text-green-600",
  },
};

const DEFAULT_ICON = {
  icon: (
    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
  ),
  bgColor: "bg-gray-100 text-gray-600",
};

interface TimelineEntryProps {
  entry: TimelineEntryType;
}

export default function TimelineEntryCard({ entry }: TimelineEntryProps) {
  const [expanded, setExpanded] = useState(false);

  const iconData = EVENT_ICONS[entry.event_type] || DEFAULT_ICON;

  const formattedDate = new Date(entry.occurred_at).toLocaleDateString("pt-BR", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
  });

  const formattedTime = new Date(entry.occurred_at).toLocaleTimeString("pt-BR", {
    hour: "2-digit",
    minute: "2-digit",
  });

  return (
    <div
      className="flex gap-3 group cursor-pointer"
      onClick={() => setExpanded(!expanded)}
    >
      {/* Icon */}
      <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${iconData.bgColor}`}>
        {iconData.icon}
      </div>

      {/* Content */}
      <div className="flex-1 min-w-0 pb-4">
        <div className="bg-white rounded-lg border shadow-sm p-3 hover:shadow-md transition-shadow">
          <div className="flex items-start justify-between gap-2">
            <p className="text-sm text-gray-900 font-medium leading-snug">
              {entry.summary}
            </p>
            <svg
              className={`w-4 h-4 text-gray-400 shrink-0 transition-transform ${expanded ? "rotate-180" : ""}`}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </div>

          <div className="flex items-center gap-3 mt-1.5 text-xs text-gray-500">
            {entry.provider_name && (
              <span className="flex items-center gap-1">
                <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
                {entry.provider_name}
              </span>
            )}
            <span>{formattedDate} as {formattedTime}</span>
          </div>

          {/* Expanded metadata */}
          {expanded && entry.metadata && Object.keys(entry.metadata).length > 0 && (
            <div className="mt-3 pt-3 border-t text-xs text-gray-600 space-y-1">
              {Object.entries(entry.metadata).map(([key, value]) => (
                <div key={key} className="flex gap-2">
                  <span className="font-medium text-gray-500 uppercase">{key}:</span>
                  <span>{String(value)}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
