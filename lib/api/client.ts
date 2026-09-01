import type { ApiErrorResponse, ApiFieldErrors } from "@/lib/types/api";

const DEFAULT_TIMEOUT_MS = 8_000;

type NextRequestOptions = {
  revalidate?: number;
  tags?: string[];
};

export type ApiRequestOptions = RequestInit & {
  next?: NextRequestOptions;
  timeoutMs?: number;
};

export class ApiRequestError extends Error {
  readonly code: string;
  readonly fields: ApiFieldErrors;
  readonly status: number;

  constructor({
    code,
    detail,
    fields = {},
    status = 0,
  }: {
    code: string;
    detail: string;
    fields?: ApiFieldErrors;
    status?: number;
  }) {
    super(detail);
    this.name = "ApiRequestError";
    this.code = code;
    this.fields = fields;
    this.status = status;
  }
}

const normalizeBaseUrl = (value: string) => value.replace(/\/+$/, "");

export function getApiBaseUrl(): string {
  const configured =
    typeof window === "undefined"
      ? process.env.API_BASE_URL ?? process.env.NEXT_PUBLIC_API_BASE_URL
      : process.env.NEXT_PUBLIC_API_BASE_URL;

  if (!configured) {
    throw new ApiRequestError({
      code: "configuration_error",
      detail: "The BeanCo API URL is not configured.",
    });
  }

  return normalizeBaseUrl(configured);
}

function isApiErrorResponse(value: unknown): value is ApiErrorResponse {
  if (!value || typeof value !== "object") return false;
  const candidate = value as Partial<ApiErrorResponse>;
  return typeof candidate.code === "string" && typeof candidate.detail === "string";
}

async function readJson(response: Response): Promise<unknown> {
  const text = await response.text();
  if (!text) return null;

  try {
    return JSON.parse(text) as unknown;
  } catch {
    return null;
  }
}

export async function apiRequest<T>(
  path: string,
  { timeoutMs = DEFAULT_TIMEOUT_MS, headers, ...options }: ApiRequestOptions = {},
): Promise<T> {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), timeoutMs);

  try {
    const response = await fetch(`${getApiBaseUrl()}/${path.replace(/^\/+/, "")}`, {
      ...options,
      headers: {
        Accept: "application/json",
        ...(options.body ? { "Content-Type": "application/json" } : {}),
        ...headers,
      },
      signal: controller.signal,
    });
    const payload = await readJson(response);

    if (!response.ok) {
      if (isApiErrorResponse(payload)) {
        throw new ApiRequestError({ ...payload, status: response.status });
      }
      throw new ApiRequestError({
        code: "request_error",
        detail: "BeanCo could not complete this request.",
        status: response.status,
      });
    }

    return payload as T;
  } catch (error) {
    if (error instanceof ApiRequestError) throw error;
    if (error instanceof DOMException && error.name === "AbortError") {
      throw new ApiRequestError({
        code: "timeout",
        detail: "The BeanCo API took too long to respond.",
      });
    }
    throw new ApiRequestError({
      code: "network_error",
      detail: "BeanCo could not reach the API. Check your connection and try again.",
    });
  } finally {
    clearTimeout(timeout);
  }
}
