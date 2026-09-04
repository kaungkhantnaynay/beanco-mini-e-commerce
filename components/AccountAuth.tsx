"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useEffect, useState } from "react";
import Button from "@/components/Button";
import {
  confirmPasswordReset,
  login,
  register,
  requestPasswordReset,
  verifyEmail,
} from "@/lib/api/account";
import { ApiRequestError } from "@/lib/api/client";

type Mode = "login" | "register" | "forgot" | "reset" | "verify";

const inputClass =
  "mt-2 h-11 w-full rounded-md border bg-background px-3 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring";

const headings: Record<Mode, string> = {
  login: "Sign in",
  register: "Create your account",
  forgot: "Reset your password",
  reset: "Choose a new password",
  verify: "Verify your email",
};

export default function AccountAuth({
  mode,
  uid = "",
  token = "",
}: {
  mode: Mode;
  uid?: string;
  token?: string;
}) {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(mode === "verify");

  useEffect(() => {
    if (mode !== "verify") return;
    if (!uid || !token) {
      setBusy(false);
      setError("This verification link is incomplete.");
      return;
    }
    void verifyEmail(uid, token)
      .then((result) => setMessage(result.detail))
      .catch((caught) =>
        setError(caught instanceof ApiRequestError ? caught.message : "Email verification failed."),
      )
      .finally(() => setBusy(false));
  }, [mode, token, uid]);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    setError("");
    setMessage("");
    try {
      if (mode === "login") {
        await login(email, password);
        router.push("/account");
        router.refresh();
      } else if (mode === "register") {
        const result = await register({
          email,
          password,
          first_name: firstName,
          last_name: lastName,
        });
        setMessage(result.detail);
      } else if (mode === "forgot") {
        setMessage((await requestPasswordReset(email)).detail);
      } else if (mode === "reset") {
        if (!uid || !token) throw new Error("This password-reset link is incomplete.");
        setMessage((await confirmPasswordReset(uid, token, password)).detail);
        setPassword("");
      }
    } catch (caught) {
      setError(
        caught instanceof ApiRequestError || caught instanceof Error
          ? caught.message
          : "BeanCo could not complete this request.",
      );
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="mx-auto max-w-md rounded-xl border bg-card p-6 shadow-sm sm:p-8">
      <h1 className="text-3xl font-bold tracking-tight">{headings[mode]}</h1>
      {mode === "verify" ? (
        <div className="mt-6">
          {busy ? <p role="status">Checking your verification link…</p> : null}
          {message ? <p className="rounded-md bg-accent/15 p-4 text-sm" role="status">{message}</p> : null}
          {error ? <p className="rounded-md bg-destructive/10 p-4 text-sm text-destructive" role="alert">{error}</p> : null}
          {!busy ? <Link className="mt-6 inline-block font-medium text-primary underline" href="/account/login">Continue to sign in</Link> : null}
        </div>
      ) : (
        <form className="mt-6 space-y-5" onSubmit={submit}>
          {mode === "register" ? (
            <div className="grid gap-4 sm:grid-cols-2">
              <label className="text-sm font-medium">First name<input className={inputClass} autoComplete="given-name" value={firstName} onChange={(event) => setFirstName(event.target.value)} /></label>
              <label className="text-sm font-medium">Last name<input className={inputClass} autoComplete="family-name" value={lastName} onChange={(event) => setLastName(event.target.value)} /></label>
            </div>
          ) : null}
          {mode !== "reset" ? (
            <label className="block text-sm font-medium">Email<input className={inputClass} type="email" required autoComplete="email" value={email} onChange={(event) => setEmail(event.target.value)} /></label>
          ) : null}
          {mode === "login" || mode === "register" || mode === "reset" ? (
            <label className="block text-sm font-medium">{mode === "reset" ? "New password" : "Password"}<input className={inputClass} type="password" required minLength={8} maxLength={128} autoComplete={mode === "login" ? "current-password" : "new-password"} value={password} onChange={(event) => setPassword(event.target.value)} /></label>
          ) : null}
          <Button className="w-full" type="submit" disabled={busy} aria-busy={busy}>{busy ? "Please wait…" : headings[mode]}</Button>
          {message ? <p className="rounded-md bg-accent/15 p-4 text-sm" role="status">{message}</p> : null}
          {error ? <p className="rounded-md bg-destructive/10 p-4 text-sm text-destructive" role="alert">{error}</p> : null}
        </form>
      )}
      <div className="mt-6 flex flex-wrap gap-x-4 gap-y-2 text-sm">
        {mode !== "login" ? <Link className="text-primary underline" href="/account/login">Sign in</Link> : null}
        {mode === "login" ? <Link className="text-primary underline" href="/account/register">Create account</Link> : null}
        {mode === "login" ? <Link className="text-primary underline" href="/account/forgot-password">Forgot password?</Link> : null}
      </div>
    </section>
  );
}
