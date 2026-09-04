"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useCallback, useEffect, useState, type FormEvent } from "react";
import Button from "@/components/Button";
import {
  createSavedAddress,
  deleteSavedAddress,
  getAccount,
  getAccountOrders,
  getSavedAddresses,
  logout,
  updateProfile,
  updateSavedAddress,
} from "@/lib/api/account";
import { ApiRequestError } from "@/lib/api/client";
import { formatTHB } from "@/lib/format";
import type { Account, OrderStatusResponse, SavedAddress, SavedAddressInput } from "@/lib/types/api";

const inputClass = "mt-1 h-10 w-full rounded-md border bg-background px-3 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring";
const blankAddress: SavedAddressInput = { label: "Home", is_default: false, full_name: "", phone: "", address_line_1: "", address_line_2: "", subdistrict: "", district: "", province: "", postal_code: "", country_code: "TH" };
const addressFields: Array<{ name: keyof SavedAddressInput; label: string; optional?: boolean }> = [
  { name: "label", label: "Label" }, { name: "full_name", label: "Full name" },
  { name: "phone", label: "Phone" }, { name: "address_line_1", label: "Address" },
  { name: "address_line_2", label: "Apartment, suite, etc.", optional: true },
  { name: "subdistrict", label: "Subdistrict" }, { name: "district", label: "District" },
  { name: "province", label: "Province" }, { name: "postal_code", label: "Postal code" },
];

export default function AccountDashboard() {
  const router = useRouter();
  const [account, setAccount] = useState<Account | null>(null);
  const [addresses, setAddresses] = useState<SavedAddress[]>([]);
  const [orders, setOrders] = useState<OrderStatusResponse[]>([]);
  const [address, setAddress] = useState<SavedAddressInput>(blankAddress);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const [nextAccount, nextAddresses, nextOrders] = await Promise.all([
        getAccount(), getSavedAddresses(), getAccountOrders(),
      ]);
      setAccount(nextAccount); setAddresses(nextAddresses); setOrders(nextOrders.results);
    } catch (caught) {
      setError(caught instanceof ApiRequestError ? caught.message : "Your account could not be loaded.");
    } finally { setLoading(false); }
  }, []);

  useEffect(() => { void load(); }, [load]);

  async function saveProfile(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); if (!account) return; setBusy(true); setError("");
    try { setAccount(await updateProfile(account)); setMessage("Profile updated."); }
    catch (caught) { setError(caught instanceof ApiRequestError ? caught.message : "Profile could not be updated."); }
    finally { setBusy(false); }
  }

  async function saveAddress(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setBusy(true); setError("");
    try {
      if (editingId) await updateSavedAddress(editingId, address); else await createSavedAddress(address);
      setAddress(blankAddress); setEditingId(null); setMessage(editingId ? "Address updated." : "Address saved.");
      setAddresses(await getSavedAddresses());
    } catch (caught) { setError(caught instanceof ApiRequestError ? caught.message : "Address could not be saved."); }
    finally { setBusy(false); }
  }

  function editAddress(item: SavedAddress) {
    const { public_id: _publicId, created_at: _created, updated_at: _updated, ...input } = item;
    void _publicId; void _created; void _updated;
    setEditingId(item.public_id); setAddress(input); setMessage("");
  }

  async function removeAddress(publicId: string) {
    setBusy(true); setError("");
    try { await deleteSavedAddress(publicId); setAddresses(await getSavedAddresses()); setMessage("Address removed."); }
    catch (caught) { setError(caught instanceof ApiRequestError ? caught.message : "Address could not be removed."); }
    finally { setBusy(false); }
  }

  async function signOut() {
    setBusy(true);
    try { await logout(); router.push("/"); router.refresh(); }
    catch (caught) { setError(caught instanceof ApiRequestError ? caught.message : "Sign out failed."); setBusy(false); }
  }

  if (loading) return <p role="status" className="rounded-xl border bg-card p-8">Loading your account…</p>;
  if (!account) return <section className="rounded-xl border bg-card p-8"><h1 className="text-3xl font-bold">Your account</h1><p className="mt-3 text-muted-foreground">{error || "Please sign in to continue."}</p><Link className="mt-5 inline-block font-medium text-primary underline" href="/account/login">Sign in</Link></section>;

  return <div className="space-y-10">
    <div className="flex flex-wrap items-start justify-between gap-4"><div><h1 className="text-4xl font-bold tracking-tight">Your account</h1><p className="mt-2 text-muted-foreground">{account.email}</p></div><Button variant="outline" onClick={() => void signOut()} disabled={busy}>Sign out</Button></div>
    {message ? <p className="rounded-md bg-accent/15 p-4 text-sm" role="status">{message}</p> : null}
    {error ? <p className="rounded-md bg-destructive/10 p-4 text-sm text-destructive" role="alert">{error}</p> : null}
    <section className="rounded-xl border bg-card p-6"><h2 className="text-xl font-semibold">Profile</h2><form className="mt-5 grid gap-4 sm:grid-cols-2" onSubmit={saveProfile}><label className="text-sm font-medium">First name<input className={inputClass} value={account.first_name} onChange={(event) => setAccount({ ...account, first_name: event.target.value })} /></label><label className="text-sm font-medium">Last name<input className={inputClass} value={account.last_name} onChange={(event) => setAccount({ ...account, last_name: event.target.value })} /></label><div className="sm:col-span-2"><Button disabled={busy}>Save profile</Button></div></form></section>
    <section className="rounded-xl border bg-card p-6"><h2 className="text-xl font-semibold">Saved addresses</h2><div className="mt-5 grid gap-4 lg:grid-cols-2">{addresses.map((item) => <article className="rounded-lg border p-4" key={item.public_id}><div className="flex justify-between gap-3"><h3 className="font-semibold">{item.label}</h3>{item.is_default ? <span className="text-xs font-semibold text-primary">Default</span> : null}</div><p className="mt-2 text-sm text-muted-foreground">{item.full_name}<br />{item.address_line_1}<br />{item.district}, {item.province} {item.postal_code}<br />{item.phone}</p><div className="mt-4 flex gap-2"><Button type="button" size="sm" variant="outline" onClick={() => editAddress(item)}>Edit</Button><Button type="button" size="sm" variant="ghost" disabled={busy} onClick={() => void removeAddress(item.public_id)}>Remove</Button></div></article>)}</div>
      <form className="mt-8 grid gap-4 sm:grid-cols-2" onSubmit={saveAddress}><h3 className="text-lg font-semibold sm:col-span-2">{editingId ? "Edit address" : "Add an address"}</h3>{addressFields.map((field) => <label className={`text-sm font-medium ${field.name.startsWith("address_line") ? "sm:col-span-2" : ""}`} key={field.name}>{field.label}<input className={inputClass} required={!field.optional} value={String(address[field.name])} onChange={(event) => setAddress({ ...address, [field.name]: event.target.value })} /></label>)}<label className="flex items-center gap-2 text-sm sm:col-span-2"><input type="checkbox" checked={address.is_default} onChange={(event) => setAddress({ ...address, is_default: event.target.checked })} />Use as my default address</label><div className="flex gap-2 sm:col-span-2"><Button disabled={busy}>{editingId ? "Update address" : "Save address"}</Button>{editingId ? <Button type="button" variant="ghost" onClick={() => { setEditingId(null); setAddress(blankAddress); }}>Cancel</Button> : null}</div></form>
    </section>
    <section className="rounded-xl border bg-card p-6"><h2 className="text-xl font-semibold">Order history</h2>{orders.length ? <div className="mt-5 divide-y rounded-lg border">{orders.map((order) => <Link className="flex flex-wrap items-center justify-between gap-3 p-4 hover:bg-muted" href={`/account/orders/${order.public_id}`} key={order.public_id}><span><span className="block text-sm font-semibold">{order.public_id}</span><span className="text-xs text-muted-foreground">{new Intl.DateTimeFormat("en-TH", { dateStyle: "medium" }).format(new Date(order.created_at))}</span></span><span className="text-sm font-semibold">{formatTHB(order.total)} · {order.status.replaceAll("_", " ")}</span></Link>)}</div> : <p className="mt-4 text-sm text-muted-foreground">You have no account orders yet.</p>}</section>
  </div>;
}
