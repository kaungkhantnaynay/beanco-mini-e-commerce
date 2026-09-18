import type { NextConfig } from "next";

import { getAllowedDevOrigins } from "./lib/config/dev-origins";

const mediaBaseUrl = new URL(
  process.env.NEXT_PUBLIC_MEDIA_BASE_URL ?? "http://localhost:8000/media",
);
const allowedDevOrigins = getAllowedDevOrigins();

const nextConfig: NextConfig = {
  agentRules: false,
  ...(allowedDevOrigins ? { allowedDevOrigins } : {}),
  output: "standalone",
  images: {
    dangerouslyAllowLocalIP: process.env.NODE_ENV !== "production",
    remotePatterns: [
      {
        protocol: "https",
        hostname: "images.unsplash.com",
      },
      {
        protocol: "https",
        hostname: "beanco-mini-e-commerce.vercel.app",
        pathname: "/images/**",
      },
      {
        protocol: mediaBaseUrl.protocol.replace(":", "") as "http" | "https",
        hostname: mediaBaseUrl.hostname,
        port: mediaBaseUrl.port,
        pathname: `${mediaBaseUrl.pathname.replace(/\/$/, "")}/**`,
      },
    ],
  },
};

export default nextConfig;
