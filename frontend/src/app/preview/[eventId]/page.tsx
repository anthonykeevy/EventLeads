export default function PreviewPage({ params }: { params: { eventId: string } }) {
  return (
    <main className="min-h-screen p-6">
      <h1 className="text-xl font-semibold mb-4">Preview • Event {params.eventId}</h1>
      <div className="bg-white w-[960px] aspect-video border shadow-sm flex items-center justify-center text-neutral-400">
        Rendered layout (read-only)
      </div>
    </main>
  );
}



