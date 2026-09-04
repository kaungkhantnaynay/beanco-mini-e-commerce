import AccountOrderDetail from "@/components/AccountOrderDetail";
import AccountShell from "@/components/AccountShell";

export default async function AccountOrderPage({ params }: { params: Promise<{ publicId: string }> }) {
  const { publicId } = await params;
  return <AccountShell><AccountOrderDetail publicId={publicId} /></AccountShell>;
}
