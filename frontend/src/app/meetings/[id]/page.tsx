"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";

interface Recap {
  summary: string;
  decisions: string[];
  action_items: Array<{ description: string; owner: string; due_date: string }>;
  open_questions: string[];
  key_topics: string[];
}

interface Meeting {
  id: number;
  title: string;
  start_time: string;
  duration_minutes: number;
  meeting_type: string;
  state: string;
  attendees: Array<{ name: string; email: string }>;
  recap?: Recap;
}

export default function MeetingDetailPage({ params }: { params: { id: string } }) {
  const [meeting, setMeeting] = useState<Meeting | null>(null);

  useEffect(() => {
    api.get(`/meetings/${params.id}/`).then((res) => setMeeting(res.data));
  }, [params.id]);

  if (!meeting) return <p className="text-gray-500">Loading...</p>;

  return (
    <div className="max-w-3xl">
      <h2 className="text-2xl font-bold mb-1">{meeting.title}</h2>
      <p className="text-gray-500 mb-6">
        {new Date(meeting.start_time).toLocaleString()} · {meeting.duration_minutes}min · {meeting.meeting_type}
      </p>

      {meeting.recap ? (
        <div className="space-y-6">
          <section>
            <h3 className="font-semibold text-lg mb-2">Summary</h3>
            <p className="text-gray-700 leading-relaxed">{meeting.recap.summary}</p>
          </section>

          {meeting.recap.decisions.length > 0 && (
            <section>
              <h3 className="font-semibold text-lg mb-2">Decisions</h3>
              <ul className="list-disc list-inside space-y-1">
                {meeting.recap.decisions.map((d, i) => <li key={i}>{d}</li>)}
              </ul>
            </section>
          )}

          {meeting.recap.action_items.length > 0 && (
            <section>
              <h3 className="font-semibold text-lg mb-2">Action Items</h3>
              <div className="space-y-2">
                {meeting.recap.action_items.map((a, i) => (
                  <div key={i} className="bg-blue-50 border border-blue-200 rounded p-3">
                    <p className="font-medium">{a.description}</p>
                    <p className="text-sm text-gray-600">Owner: {a.owner} · Due: {a.due_date || "TBD"}</p>
                  </div>
                ))}
              </div>
            </section>
          )}

          {meeting.recap.open_questions.length > 0 && (
            <section>
              <h3 className="font-semibold text-lg mb-2">Open Questions</h3>
              <ul className="list-disc list-inside space-y-1">
                {meeting.recap.open_questions.map((q, i) => <li key={i}>{q}</li>)}
              </ul>
            </section>
          )}
        </div>
      ) : (
        <div className="bg-yellow-50 border border-yellow-200 rounded p-4">
          <p className="text-yellow-700">Recap not yet generated. Current state: <strong>{meeting.state}</strong></p>
        </div>
      )}
    </div>
  );
}
