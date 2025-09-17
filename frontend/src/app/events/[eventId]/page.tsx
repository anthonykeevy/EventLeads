"use client";
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { createForm, listForms, type FormItem } from "@/lib/events";
import AuthGate from "@/components/AuthGate";

export default function EventFormsPage() {
  const params = useParams();
  const eventId = Number(params?.eventId);
  const [forms, setForms] = useState<FormItem[]>([]);
  const [name, setName] = useState("");
  const [busy, setBusy] = useState(false);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState<string | null>(null);

  async function refresh() {
    if (!eventId) return;
    try {
      setErr(null);
      setLoading(true);
      const rows = await listForms(eventId);
      setForms(rows);
    } catch (e: any) {
      setErr(e?.message || "Failed to load forms");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void refresh();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [eventId]);

  async function onCreate() {
    if (!name.trim()) return;
    try {
      setBusy(true);
      setErr(null);
      await createForm(eventId, name.trim());
      setName("");
      await refresh();
    } catch (e: any) {
      setErr(e?.message || "Failed to create form");
    } finally {
      setBusy(false);
    }
  }

  return (
    <AuthGate>
      <main className="p-6 space-y-4">
        <h1 className="text-2xl font-semibold">Forms for Event #{eventId}</h1>
        <div className="flex items-center gap-2">
          <input
            className="border rounded px-2 py-1"
            placeholder="New form name"
            value={name}
            onChange={(e) => setName(e.target.value)}
          />
          <button
            className="bg-blue-600 text-white px-3 py-1 rounded disabled:opacity-60"
            onClick={onCreate}
            disabled={busy || !name.trim()}
          >
            Create Form
          </button>
          <button className="px-3 py-1 rounded border" onClick={() => refresh()} disabled={loading}>
            Refresh
          </button>
          {err && <span className="text-red-600 text-sm">{err}</span>}
        </div>
        {loading ? (
          <p className="text-gray-600">Loading…</p>
        ) : forms.length === 0 ? (
          <p className="text-gray-600">No forms yet. Create your first form.</p>
        ) : (
          <ul className="space-y-2">
            {forms.map((f) => (
              <li key={f.id} className="flex items-center justify-between">
                <span>{f.name}</span>
                <span className="text-sm text-gray-500">{f.public_slug || "no-slug"}</span>
              </li>
            ))}
          </ul>
        )}
      </main>
    </AuthGate>
  );
}
