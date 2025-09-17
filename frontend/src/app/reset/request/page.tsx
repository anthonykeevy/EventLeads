"use client";
import { useState } from "react";
import { resetRequest } from "@/lib/auth";

export default function ResetRequestPage() {
  const [email, setEmail] = useState("");
  const [msg, setMsg] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setMsg(null);
    try {
      await resetRequest(email);
      setMsg("If registered, a reset email has been sent.");
    } catch (err: any) {
      setMsg(err.message || "Request failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen flex items-center justify-center p-6">
      <div className="w-full max-w-sm space-y-4">
        <h1 className="text-2xl font-semibold">Reset Password</h1>
        {msg && <div className="text-sm">{msg}</div>}
        <form onSubmit={onSubmit} className="space-y-3">
          <input className="w-full border rounded px-3 py-2" placeholder="Email" value={email} onChange={(e)=>setEmail(e.target.value)} />
          <button disabled={loading} className="w-full bg-black text-white rounded px-3 py-2">{loading? 'Sending...' : 'Send reset link'}</button>
        </form>
        <div className="text-sm text-gray-600">
          <a className="underline" href="/login">Back to login</a>
        </div>
      </div>
    </main>
  );
}

