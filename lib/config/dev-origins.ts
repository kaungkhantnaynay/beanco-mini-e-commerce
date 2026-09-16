import { networkInterfaces } from "node:os";

type NetworkAddress = {
  address: string;
  family: string | number;
  internal: boolean;
};

type NetworkInterfaceMap = Record<string, NetworkAddress[] | undefined>;

function parseConfiguredOrigins(value?: string) {
  return value
    ?.split(",")
    .map((origin) => origin.trim())
    .filter(Boolean) ?? [];
}

export function collectAllowedDevOrigins(
  interfaces: NetworkInterfaceMap,
  configuredOrigins?: string,
) {
  const localIpv4Addresses = Object.values(interfaces)
    .flatMap((addresses) => addresses ?? [])
    .filter(
      ({ family, internal }) =>
        !internal && (family === "IPv4" || family === 4),
    )
    .map(({ address }) => address);

  return [...new Set([...localIpv4Addresses, ...parseConfiguredOrigins(configuredOrigins)])];
}

export function getAllowedDevOrigins(
  environment = process.env.NODE_ENV,
  interfaces: NetworkInterfaceMap = networkInterfaces(),
  configuredOrigins = process.env.BEANCO_DEV_ALLOWED_ORIGINS,
) {
  if (environment !== "development") {
    return undefined;
  }

  return collectAllowedDevOrigins(interfaces, configuredOrigins);
}
