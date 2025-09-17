"use client";
import { useState, useEffect } from "react";
import { resetConfirm } from "@/lib/auth";
import { useSearchParams } from "next/navigation";

export default function ResetConfirmPage() {
  const searchParams = useSearchParams();
  const [token, setToken] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [msg, setMsg] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  // Auto-extract token from URL
  useEffect(() => {
    const tokenFromUrl = searchParams.get("token");
    if (tokenFromUrl) {
      setToken(tokenFromUrl);
    }
  }, [searchParams]);

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setMsg(null);
    
    // Validation
    if (!token) {
      setMsg("Token is required");
      setLoading(false);
      return;
    }
    
    if (password !== confirmPassword) {
      setMsg("Passwords do not match");
      setLoading(false);
      return;
    }
    
    if (password.length < 6) {
      setMsg("Password must be at least 6 characters");
      setLoading(false);
      return;
    }
    
    try {
      await resetConfirm(token, password);
      setMsg("Password updated successfully. You may now login.");
    } catch (err: any) {
      setMsg(err.message || "Reset failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen flex items-center justify-center p-6">
      <div className="w-full max-w-sm space-y-4">
        <h1 className="text-2xl font-semibold">Set New Password</h1>
        {msg && <div className="text-sm">{msg}</div>}
        <form onSubmit={onSubmit} className="space-y-3">
          {!token && (
            <input 
              className="w-full border rounded px-3 py-2" 
              placeholder="Reset token (from email)" 
              value={token} 
              onChange={(e)=>setToken(e.target.value)} 
            />
          )}
          <input 
            className="w-full border rounded px-3 py-2" 
            placeholder="New password" 
            type="password" 
            value={password} 
            onChange={(e)=>setPassword(e.target.value)} 
            required
          />
          <input 
            className="w-full border rounded px-3 py-2" 
            placeholder="Confirm new password" 
            type="password" 
            value={confirmPassword} 
            onChange={(e)=>setConfirmPassword(e.target.value)} 
            required
          />
          <button disabled={loading} className="w-full bg-black text-white rounded px-3 py-2">
            {loading ? 'Updating...' : 'Update password'}
          </button>
        </form>
        <div className="text-sm text-gray-600">
          <a className="underline" href="/login">Back to login</a>
        </div>
      </div>
    </main>
  );
}

