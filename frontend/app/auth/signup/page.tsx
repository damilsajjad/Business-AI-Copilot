import AuthForm from "@/components/auth-form";
import Link from "next/link";

export const metadata = {
  title: "Create Account — AI Business Copilot",
  description:
    "Create your AI Business Copilot account to start analyzing your business data with AI-powered insights.",
};

export default function SignupPage() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-zinc-50 px-4 dark:bg-zinc-950">
      <div className="w-full max-w-sm">
        {/* Logo / brand */}
        <div className="mb-8 text-center">
          <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-indigo-600 text-xl font-bold text-white">
            BC
          </div>
          <h1 className="text-xl font-semibold tracking-tight text-zinc-900 dark:text-zinc-100">
            Create your account
          </h1>
          <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">
            Get started with AI-powered business insights
          </p>
        </div>

        {/* Form card */}
        <div className="rounded-xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
          <AuthForm mode="signup" />
        </div>

        {/* Footer link */}
        <p className="mt-5 text-center text-sm text-zinc-500 dark:text-zinc-400">
          Already have an account?{" "}
          <Link
            href="/auth/login"
            className="font-medium text-indigo-600 hover:text-indigo-700 dark:text-indigo-400 dark:hover:text-indigo-300"
          >
            Sign in
          </Link>
        </p>
      </div>
    </div>
  );
}
