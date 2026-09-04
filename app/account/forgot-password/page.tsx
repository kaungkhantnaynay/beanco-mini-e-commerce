import AccountAuth from "@/components/AccountAuth";
import AccountShell from "@/components/AccountShell";

export default function ForgotPasswordPage() {
  return <AccountShell><AccountAuth mode="forgot" /></AccountShell>;
}
