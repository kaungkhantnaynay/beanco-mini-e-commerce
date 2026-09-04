import AccountAuth from "@/components/AccountAuth";
import AccountShell from "@/components/AccountShell";

export default async function VerifyEmailPage({ searchParams }: { searchParams: Promise<{ uid?: string; token?: string }> }) {
  const { uid, token } = await searchParams;
  return <AccountShell><AccountAuth mode="verify" uid={uid} token={token} /></AccountShell>;
}
