import { describe, expect, test } from "bun:test";

import { normalizeUrl } from "./url";

describe("normalizeUrl", () => {
  test("accepts HTTP and HTTPS webpages", () => {
    expect(normalizeUrl("http://example.com/path").protocol).toBe("http:");
    expect(normalizeUrl("https://example.com/path").protocol).toBe("https:");
  });

  test("rejects non-web protocols that could expose local content", () => {
    for (const input of [
      "file:///etc/passwd",
      "data:text/html,<h1>secret</h1>",
      "javascript:alert(1)",
    ]) {
      expect(() => normalizeUrl(input)).toThrow("Unsupported URL protocol");
    }
  });
});
