"use client";

import { FormEvent, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Image from "next/image";
import { getAuthToken, login, setAuthToken, signup } from "@/lib/api";

const featuredCapabilities = [
  {
    title: "Deep Retrieval Engine",
    description:
      "Context-aware chunk ranking that follows intent shifts in long questions and keeps responses grounded in uploaded evidence.",
  },
  {
    title: "Persistent Research Memory",
    description:
      "Each document keeps a durable conversation timeline, so follow-up analysis remains consistent across sessions.",
  },
  {
    title: "High-Signal Synthesis",
    description:
      "Built to produce decision-ready summaries, comparisons, and extraction outputs from dense technical documents.",
  },
  {
    title: "Production-Ready Security",
    description:
      "Token-based auth with isolated conversation access, enabling secure team workflows on sensitive files.",
  },
];

export default function LoginPage() {
  const router = useRouter();
  const [mode, setMode] = useState<"login" | "signup">("login");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (getAuthToken()) {
      router.replace("/");
    }
  }, [router]);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError("");

    const normalizedUsername = username.trim();
    if (!normalizedUsername) {
      setError("Username is required");
      return;
    }

    if (mode === "signup") {
      if (password.length < 6) {
        setError("Password must be at least 6 characters.");
        return;
      }
      if (password !== confirmPassword) {
        setError("Passwords do not match.");
        return;
      }
    }

    setIsLoading(true);
    try {
      const result =
        mode === "signup"
          ? await signup(normalizedUsername, password)
          : await login(normalizedUsername, password);
      setAuthToken(result.access_token);
      router.replace("/");
    } catch (err) {
      setError(err instanceof Error ? err.message : mode === "signup" ? "Sign up failed" : "Login failed");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main className="relative min-h-screen overflow-hidden bg-slate-950 text-slate-100">
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute -left-32 top-16 h-72 w-72 rounded-full bg-cyan-400/10 blur-3xl" />
        <div className="absolute right-0 top-0 h-96 w-96 rounded-full bg-blue-500/20 blur-3xl" />
        <div className="absolute bottom-0 left-1/3 h-72 w-72 rounded-full bg-emerald-400/10 blur-3xl" />
      </div>

      <section className="relative mx-auto grid min-h-screen w-full max-w-7xl grid-cols-1 gap-8 px-4 py-8 md:px-6 lg:grid-cols-[1.3fr_0.9fr] lg:items-center lg:gap-10 lg:px-8">
        <article className="rounded-3xl border border-white/10 bg-slate-900/45 p-6 shadow-2xl shadow-black/30 backdrop-blur md:p-8">
          <div className="mb-6 inline-flex items-center gap-3 rounded-full border border-cyan-300/30 bg-cyan-300/10 px-4 py-2 text-xs font-semibold tracking-[0.16em] text-cyan-200">
            <Image src="/logo.png" alt="DocQuest logo" width={22} height={22} className="rounded" priority />
            INTELLIGENT DOCUMENT OPS
          </div>

          <h1 className="max-w-3xl text-3xl font-semibold leading-tight text-white md:text-4xl lg:text-5xl">
            Transform dense documents into fast, high-confidence answers with DocQuest.
          </h1>

          <p className="mt-5 max-w-2xl text-sm leading-7 text-slate-300 md:text-base">
            DocQuest is built for serious analysis workflows where accuracy, continuity, and speed matter.
            Upload once, keep context over time, and get synthesis that helps you decide faster.
          </p>

          <div className="mt-8 grid grid-cols-1 gap-3 md:grid-cols-2">
            {featuredCapabilities.map((item, index) => (
              <div
                key={item.title}
                className="rounded-2xl border border-white/10 bg-slate-950/60 p-4 transition duration-300 hover:-translate-y-0.5 hover:border-cyan-300/40"
                style={{ animationDelay: `${index * 120}ms` }}
              >
                <h2 className="text-sm font-semibold text-cyan-200">{item.title}</h2>
                <p className="mt-2 text-xs leading-6 text-slate-300">{item.description}</p>
              </div>
            ))}
          </div>
        </article>

        <aside className="w-full rounded-3xl border border-white/10 bg-slate-900/80 p-6 shadow-2xl shadow-black/30 backdrop-blur md:p-7">
          <div className="mb-5 flex items-center gap-3">
            <Image src="/logo.png" alt="DocQuest logo" width={32} height={32} className="rounded" priority />
            <div>
              <h3 className="text-lg font-semibold text-white">{mode === "signup" ? "Create Account" : "Welcome Back"}</h3>
              <p className="text-xs text-slate-400">
                {mode === "signup" ? "Create your DocQuest workspace access." : "Sign in to continue your research workspace."}
              </p>
            </div>
          </div>

          <div className="mb-4 grid grid-cols-2 rounded-xl border border-slate-700 bg-slate-950 p-1">
            <button
              type="button"
              onClick={() => {
                setMode("login");
                setError("");
              }}
              className={`rounded-lg px-3 py-1.5 text-sm font-medium transition ${
                mode === "login" ? "bg-blue-600 text-white" : "text-slate-300 hover:bg-slate-800"
              }`}
            >
              Login
            </button>
            <button
              type="button"
              onClick={() => {
                setMode("signup");
                setError("");
              }}
              className={`rounded-lg px-3 py-1.5 text-sm font-medium transition ${
                mode === "signup" ? "bg-blue-600 text-white" : "text-slate-300 hover:bg-slate-800"
              }`}
            >
              Sign Up
            </button>
          </div>

          <form onSubmit={handleSubmit} className="grid gap-3">
            <label className="grid gap-1 text-sm">
              <span className="text-slate-300">Username</span>
              <input
                className="rounded-xl border border-slate-700 bg-slate-950 px-3 py-2 text-sm outline-none focus:border-blue-500"
                value={username}
                onChange={(event) => setUsername(event.target.value)}
                autoComplete="username"
                required
              />
            </label>

            <label className="grid gap-1 text-sm">
              <span className="text-slate-300">Password</span>
              <input
                type="password"
                className="rounded-xl border border-slate-700 bg-slate-950 px-3 py-2 text-sm outline-none focus:border-blue-500"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                autoComplete="current-password"
                required
              />
            </label>

            {mode === "signup" ? (
              <label className="grid gap-1 text-sm">
                <span className="text-slate-300">Confirm Password</span>
                <input
                  type="password"
                  className="rounded-xl border border-slate-700 bg-slate-950 px-3 py-2 text-sm outline-none focus:border-blue-500"
                  value={confirmPassword}
                  onChange={(event) => setConfirmPassword(event.target.value)}
                  autoComplete="new-password"
                  required
                />
              </label>
            ) : null}

            <button
              type="submit"
              disabled={isLoading}
              className="mt-2 rounded-xl bg-blue-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-blue-500 disabled:cursor-not-allowed disabled:bg-blue-600/50"
            >
              {isLoading
                ? mode === "signup"
                  ? "Creating account..."
                  : "Signing in..."
                : mode === "signup"
                  ? "Create Account"
                  : "Sign In"}
            </button>
          </form>

          {error ? <p className="mt-3 rounded-xl border border-rose-400/50 bg-rose-900/40 px-3 py-2 text-xs text-rose-100">{error}</p> : null}
        </aside>
      </section>
    </main>
  );
}
