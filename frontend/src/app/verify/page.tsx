"use client";
import { Suspense, useEffect, useState } from "react";
import { verify } from "@/lib/auth";
import { useSearchParams } from "next/navigation";

function VerifyInner() {
  const sp = useSearchParams();
  const token = sp.get("token") || "";
  const [msg, setMsg] = useState("Verifying...");

  useEffect(() => {
    if (!token) {
      setMsg("Missing token");
      return;
    }
    verify(token)
      .then(() => setMsg("Email verified. You may now login."))
      .catch((e) => setMsg(e.message || "Verification failed"));
  }, [token]);

  return (
    <main className="min-h-screen flex items-center justify-center p-6">
      <div className="w-full max-w-sm space-y-4 text-center">
        <h1 className="text-2xl font-semibold">Verify Email</h1>
        <p>{msg}</p>
        <a className="underline" href="/login">Back to login</a>
      </div>
    </main>
  );
}

export default function VerifyPage() {
  return (
    <Suspense fallback={<div className="p-6">Loading…</div>}>
      <VerifyInner />
    </Suspense>
  );
}

