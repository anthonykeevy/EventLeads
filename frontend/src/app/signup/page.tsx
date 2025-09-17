"use client";
import { useState } from "react";
import { signup } from "@/lib/auth";

export default function SignupPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [msg, setMsg] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setMsg(null);
    try {
      await signup(email, password);
      setMsg("Verification required. Check your email.");
    } catch (err: any) {
      setMsg(err.message || "Signup failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen flex items-center justify-center p-6">
      <div className="w-full max-w-sm space-y-4">
        <h1 className="text-2xl font-semibold">Sign up</h1>
        {msg && <div className="text-blue-600 text-sm">{msg}</div>}
        <form onSubmit={onSubmit} className="space-y-3">
          <input className="w-full border rounded px-3 py-2" placeholder="Email" value={email} onChange={(e)=>setEmail(e.target.value)} />
          <input className="w-full border rounded px-3 py-2" placeholder="Password" type="password" value={password} onChange={(e)=>setPassword(e.target.value)} />
          <button disabled={loading} className="w-full bg-black text-white rounded px-3 py-2">{loading? 'Creating...' : 'Create account'}</button>
        </form>
        <div className="text-sm text-gray-600">
          <a className="underline" href="/login">Back to login</a>
        </div>
      </div>
    </main>
  );
}

