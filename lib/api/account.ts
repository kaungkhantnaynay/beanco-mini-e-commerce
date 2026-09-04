import { apiRequest } from "@/lib/api/client";
import type {
  Account,
  Order,
  OrderStatusResponse,
  PaginatedResponse,
  SavedAddress,
  SavedAddressInput,
  SubmissionResponse,
} from "@/lib/types/api";

const browserOptions = { cache: "no-store" as const, credentials: "include" as const };

function cookieValue(name: string): string {
  if (typeof document === "undefined") return "";
  const prefix = `${encodeURIComponent(name)}=`;
  const match = document.cookie.split("; ").find((part) => part.startsWith(prefix));
  return match ? decodeURIComponent(match.slice(prefix.length)) : "";
}

async function csrfHeaders(): Promise<Record<string, string>> {
  await apiRequest<SubmissionResponse>("auth/csrf/", browserOptions);
  const cookieName = process.env.NEXT_PUBLIC_CSRF_COOKIE_NAME ?? "beanco_csrftoken";
  const token = cookieValue(cookieName);
  return token ? { "X-CSRFToken": token } : {};
}

async function accountMutation<T>(
  path: string,
  method: "POST" | "PATCH" | "DELETE",
  body?: unknown,
): Promise<T> {
  return apiRequest<T>(path, {
    ...browserOptions,
    method,
    headers: await csrfHeaders(),
    ...(body === undefined ? {} : { body: JSON.stringify(body) }),
  });
}

export function register(input: {
  email: string;
  password: string;
  first_name: string;
  last_name: string;
}): Promise<SubmissionResponse> {
  return accountMutation("auth/register/", "POST", input);
}

export function verifyEmail(uid: string, token: string): Promise<SubmissionResponse> {
  return accountMutation("auth/verify-email/", "POST", { uid, token });
}

export function login(email: string, password: string): Promise<Account> {
  return accountMutation("auth/login/", "POST", { email, password });
}

export function logout(): Promise<SubmissionResponse> {
  return accountMutation("auth/logout/", "POST");
}

export function requestPasswordReset(email: string): Promise<SubmissionResponse> {
  return accountMutation("auth/password-reset/", "POST", { email });
}

export function confirmPasswordReset(
  uid: string,
  token: string,
  newPassword: string,
): Promise<SubmissionResponse> {
  return accountMutation("auth/password-reset/confirm/", "POST", {
    uid,
    token,
    new_password: newPassword,
  });
}

export function getAccount(): Promise<Account> {
  return apiRequest<Account>("account/", browserOptions);
}

export function updateProfile(input: Pick<Account, "first_name" | "last_name">): Promise<Account> {
  return accountMutation("account/", "PATCH", input);
}

export function getSavedAddresses(): Promise<SavedAddress[]> {
  return apiRequest<SavedAddress[]>("account/addresses/", browserOptions);
}

export function createSavedAddress(input: SavedAddressInput): Promise<SavedAddress> {
  return accountMutation("account/addresses/", "POST", input);
}

export function updateSavedAddress(
  publicId: string,
  input: Partial<SavedAddressInput>,
): Promise<SavedAddress> {
  return accountMutation(`account/addresses/${publicId}/`, "PATCH", input);
}

export async function deleteSavedAddress(publicId: string): Promise<void> {
  await accountMutation<null>(`account/addresses/${publicId}/`, "DELETE");
}

export function getAccountOrders(): Promise<PaginatedResponse<OrderStatusResponse>> {
  return apiRequest<PaginatedResponse<OrderStatusResponse>>("account/orders/", browserOptions);
}

export function getAccountOrder(publicId: string): Promise<Order> {
  return apiRequest<Order>(`account/orders/${publicId}/`, browserOptions);
}

export function cancelAccountOrder(publicId: string): Promise<Order> {
  return accountMutation(`account/orders/${publicId}/cancel/`, "POST");
}
