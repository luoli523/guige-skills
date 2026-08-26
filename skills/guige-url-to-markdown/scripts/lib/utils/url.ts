export function normalizeUrl(input: string): URL {
  let url: URL;
  try {
    url = new URL(input);
  } catch {
    throw new Error(`Invalid URL: ${input}`);
  }

  if (url.protocol !== "http:" && url.protocol !== "https:") {
    throw new Error(`Unsupported URL protocol: ${url.protocol}`);
  }
  return url;
}

export function sanitizeFilename(input: string): string {
  return input.replace(/[^a-zA-Z0-9._-]+/g, "-").replace(/^-+|-+$/g, "") || "document";
}
