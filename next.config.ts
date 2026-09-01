import type { NextConfig } from "next";

const mediaBaseUrl = new URL(
  process.env.NEXT_PUBLIC_MEDIA_BASE_URL ?? "http://localhost:8000/media",
);

const nextConfig: NextConfig = {
  agentRules: false,
  images: {
    dangerouslyAllowLocalIP: process.env.NODE_ENV !== "production",
    remotePatterns: [
      {
        protocol: "https",
        hostname: "images.unsplash.com",
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
