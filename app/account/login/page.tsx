import AccountAuth from "@/components/AccountAuth";
import AccountShell from "@/components/AccountShell";

export default function LoginPage() {
  return <AccountShell><AccountAuth mode="login" /></AccountShell>;
}
