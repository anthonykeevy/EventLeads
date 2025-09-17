import Link from "next/link";

export default function EventsPage() {
  const events = [{ id: 1, name: "Sample Event" }];
  return (
    <main className="p-6 space-y-4">
      <h1 className="text-2xl font-semibold">Events</h1>
      <ul className="space-y-2">
        {events.map((e) => (
          <li key={e.id} className="flex items-center justify-between">
            <span>{e.name}</span>
            <div className="space-x-2">
              <Link className="underline" href={`/builder/${e.id}`}>Builder</Link>
              <Link className="underline" href={`/preview/${e.id}`}>Preview</Link>
            </div>
          </li>
        ))}
      </ul>
    </main>
  );
}



