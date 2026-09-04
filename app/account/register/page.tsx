import AccountAuth from "@/components/AccountAuth";
import AccountShell from "@/components/AccountShell";

export default function RegisterPage() {
  return <AccountShell><AccountAuth mode="register" /></AccountShell>;
}
