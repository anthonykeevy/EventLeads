"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { getToken, me, clearToken } from "@/lib/auth";
import { listEvents, type EventItem } from "@/lib/events";

export default function Home() {
  const [profile, setProfile] = useState<any>(null);
  const [events, setEvents] = useState<EventItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadingEvents, setLoadingEvents] = useState(true);
  const router = useRouter();

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const token = getToken();
        if (!token) {
          router.push("/login");
          return;
        }
        const userProfile = await me();
        setProfile(userProfile);
      } catch (err) {
        clearToken();
        router.push("/login");
      } finally {
        setLoading(false);
      }
    };

    checkAuth();
  }, [router]);

  useEffect(() => {
    const loadEvents = async () => {
      try {
        setLoadingEvents(true);
        const rows = await listEvents();
        setEvents(rows.slice(0, 5));
      } catch {
        setEvents([]);
      } finally {
        setLoadingEvents(false);
      }
    };
    if (!loading) void loadEvents();
  }, [loading]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen p-6 bg-gray-50">
      <div className="max-w-4xl mx-auto space-y-6">
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Dashboard</h1>
          <p className="text-gray-600">Welcome to the Event Form Builder</p>
        </div>

        <div className="bg-white rounded-lg shadow-sm border p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Recent Events</h2>
          {loadingEvents ? (
            <p className="text-gray-600">Loading…</p>
          ) : events.length === 0 ? (
            <p className="text-gray-600">No events yet. Create your first one.</p>
          ) : (
            <ul className="space-y-2">
              {events.map((e) => (
                <li key={e.id} className="flex items-center justify-between">
                  <span>{e.name}</span>
                  <button
                    className="text-blue-600 underline"
                    onClick={() => router.push(`/events/${e.id}`)}
                  >
                    View Forms
                  </button>
                </li>
              ))}
            </ul>
          )}
          <div className="mt-4">
            <button
              onClick={() => router.push("/events")}
              className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
            >
              Go to Events
            </button>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">User Profile</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-gray-50 p-4 rounded-md">
              <div className="text-sm text-gray-500">User ID</div>
              <div className="font-medium">{profile?.user_id || "N/A"}</div>
            </div>
            <div className="bg-gray-50 p-4 rounded-md">
              <div className="text-sm text-gray-500">Organization ID</div>
              <div className="font-medium">{profile?.org_id || "N/A"}</div>
            </div>
            <div className="bg-gray-50 p-4 rounded-md">
              <div className="text-sm text-gray-500">Role</div>
              <div className="font-medium">{profile?.role || "N/A"}</div>
            </div>
          </div>
        </div>

        <div className="text-center">
          <button
            onClick={() => {
              clearToken();
              router.push("/login");
            }}
            className="bg-red-600 text-white px-4 py-2 rounded-md hover:bg-red-700"
          >
            Sign Out
          </button>
        </div>
      </div>
    </div>
  );
}
