import Link from "next/link";

export default function Home() {
  return (
    <div className="text-center py-20">
      <h2 className="text-3xl font-bold mb-4">ACDC Teams AI Notetaker</h2>
      <p className="text-gray-600 mb-8 max-w-xl mx-auto">
        Autonomous meeting intelligence. Every Teams meeting, automatically
        summarized with decisions, action items, and follow-up reminders.
      </p>
      <Link
        href="/meetings"
        className="inline-block bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition"
      >
        View Meetings
      </Link>
    </div>
  );
}
