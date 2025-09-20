"use client";

import { useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";

function joinApi(path: string): string {
  const base = (process.env.NEXT_PUBLIC_API_BASE || "").replace(/\/$/, "");
  const p = path.startsWith("/") ? path : `/${path}`;
  return `${base}${p}`;
}

export default function AcceptInvitePage() {
  const router = useRouter();
  const [token, setToken] = useState<string>("");
  const [password, setPassword] = useState<string>("");
  const [password2, setPassword2] = useState<string>("");
  const [submitting, setSubmitting] = useState(false);
  const [message, setMessage] = useState<string>("");
  const [error, setError] = useState<string>("");
  const [inviteeEmail, setInviteeEmail] = useState<string>("");
  const [inviterName, setInviterName] = useState<string>("");

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const t = params.get("token") || "";
    setToken(t);
  }, []);

  useEffect(() => {
    const load = async () => {
      if (!token) return;
      try {
        const resp = await fetch(joinApi(`/invitations/${encodeURIComponent(token)}/preview`));
        if (resp.ok) {
          const data = await resp.json();
          setInviteeEmail(data.email || "");
          setInviterName(data.inviter_name || "Admin");
        }
      } catch {}
    };
    load();
  }, [token]);

  const passwordTooShort = useMemo(() => password.length > 0 && password.length < 8, [password]);
  const passwordMismatch = useMemo(() => password2.length > 0 && password !== password2, [password, password2]);

  const disabled = useMemo(() => {
    return !token || !password || password.length < 8 || password !== password2 || submitting;
  }, [token, password, password2, submitting]);

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setError("");
    setMessage("");
    try {
      const resp = await fetch(joinApi(`/invitations/${encodeURIComponent(token)}/accept`), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ password }),
      });
      if (resp.ok) {
        setMessage("Invitation accepted. Your password has been set. You may now sign in.");
        // short pause then redirect to login with email prefill
        setTimeout(() => {
          const emailParam = inviteeEmail ? `?email=${encodeURIComponent(inviteeEmail)}` : "";
          router.push(`/login${emailParam}`);
        }, 1500);
      } else if (resp.status === 410) {
        setError("This invitation link has expired. Please ask your admin to resend the invitation.");
      } else if (resp.status === 404) {
        setError("This invitation link is invalid. Please check the link or request a new one.");
      } else {
        const data = await resp.json().catch(() => ({}));
        setError(data?.detail || "Something went wrong. Please try again.");
      }
    } catch (err: any) {
      setError("Unable to reach the server. Please try again.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="mx-auto max-w-md p-6">
      <h1 className="text-2xl font-semibold mb-2">Accept your invitation</h1>
      <p className="text-sm text-gray-600 mb-3">
        {inviteeEmail ? (
          <>
            Hi <strong>{inviteeEmail}</strong>.
          </>
        ) : (
          <>Welcome.</>
        )}
      </p>
      <p className="text-sm text-gray-600 mb-6">
        Thanks for accepting the invitation sent by <strong>{inviterName || "your admin"}</strong>. Please set your password below. When you sign in next, use your email address and the password you set now.
      </p>

      {message && (
        <div className="rounded-md bg-green-50 text-green-700 p-3 mb-4">{message}</div>
      )}
      {error && (
        <div className="rounded-md bg-red-50 text-red-700 p-3 mb-4">{error}</div>
      )}

      <form onSubmit={onSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-1">New password</label>
          <input
            type="password"
            className="w-full border rounded-md px-3 py-2"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            minLength={8}
            required
          />
          {passwordTooShort && (
            <p className="text-xs text-red-600 mt-1">Password must be at least 8 characters.</p>
          )}
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Confirm password</label>
          <input
            type="password"
            className="w-full border rounded-md px-3 py-2"
            value={password2}
            onChange={(e) => setPassword2(e.target.value)}
            minLength={8}
            required
          />
          {passwordMismatch && (
            <p className="text-xs text-red-600 mt-1">Passwords do not match.</p>
          )}
        </div>
        <button
          type="submit"
          disabled={disabled}
          className="bg-blue-600 text-white px-4 py-2 rounded-md disabled:opacity-50"
        >
          {submitting ? "Submitting…" : "Accept invitation"}
        </button>
      </form>
    </div>
  );
}
