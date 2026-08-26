import { describe, expect, test } from "bun:test";

import { HELP_TEXT, parseArgs } from "./cli";

describe("guige-fetch CLI", () => {
  test("uses the Gui Ge command name and configuration namespace", () => {
    expect(HELP_TEXT).toContain("guige-fetch - Read a URL");
    expect(HELP_TEXT).toContain("GUIGE_CHROME_PROFILE_DIR");
    expect(HELP_TEXT).not.toContain("baoyu-fetch");
    expect(HELP_TEXT).not.toContain("BAOYU_CHROME_PROFILE_DIR");
  });

  test("parses conversion, browser, and interaction options", () => {
    const options = parseArgs([
      "bun",
      "cli.ts",
      "https://example.com/article",
      "--format",
      "json",
      "--adapter",
      "generic",
      "--output",
      "article.json",
      "--download-media",
      "--wait-for",
      "interaction",
      "--timeout",
      "45000",
    ]);

    expect(options).toMatchObject({
      url: "https://example.com/article",
      format: "json",
      adapter: "generic",
      output: "article.json",
      downloadMedia: true,
      waitMode: "interaction",
      timeoutMs: 45_000,
    });
  });

  test("rejects unknown options", () => {
    expect(() => parseArgs(["bun", "cli.ts", "--unknown"])).toThrow(
      "Unknown option: --unknown",
    );
  });
});
