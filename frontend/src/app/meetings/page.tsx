"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";

interface Meeting {
  id: number;
  title: string;
  start_time: string;
  duration_minutes: number;
  meeting_type: string;
  state: string;
  has_recap: boolean;
}

export default function MeetingsPage() {
  const [meetings, setMeetings] = useState<Meeting[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get("/meetings/").then((res) => {
      setMeetings(res.data.results || res.data);
      setLoading(false);
    });
  }, []);

  if (loading) return <p className="text-gray-500">Loading meetings...</p>;

  return (
    <div>
      <h2 className="text-2xl font-bold mb-6">Meetings</h2>
      <div className="space-y-3">
        {meetings.map((m) => (
          <Link
            key={m.id}
            href={`/meetings/${m.id}`}
            className="block bg-white border border-gray-200 rounded-lg p-4 hover:border-blue-400 transition"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">{m.title}</p>
                <p className="text-sm text-gray-500">
                  {new Date(m.start_time).toLocaleString()} · {m.duration_minutes}min
                </p>
              </div>
              <div className="flex gap-2 items-center">
                <span className="text-xs px-2 py-1 bg-gray-100 rounded">{m.meeting_type}</span>
                {m.has_recap && (
                  <span className="text-xs px-2 py-1 bg-blue-100 text-blue-700 rounded">Recap ready</span>
                )}
                <span
                  className={`text-xs px-2 py-1 rounded ${
                    m.state === "completed"
                      ? "bg-green-100 text-green-700"
                      : m.state === "failed"
                      ? "bg-red-100 text-red-700"
                      : "bg-yellow-100 text-yellow-700"
                  }`}
                >
                  {m.state}
                </span>
              </div>
            </div>
          </Link>
        ))}
        {meetings.length === 0 && (
          <p className="text-gray-500">No meetings found.</p>
        )}
      </div>
    </div>
  );
}
