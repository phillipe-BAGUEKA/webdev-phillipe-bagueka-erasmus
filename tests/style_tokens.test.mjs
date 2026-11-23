import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { join } from "node:path";
import test from "node:test";

test("AC-45 shared colors, spacing, type and radii use defined tokens", () => {
  const stylesheet = readFileSync(join("src", "static", "css", "app.css"), "utf8");
  const rootBlock = stylesheet.match(/:root\s*\{([^}]+)\}/);
  assert.ok(rootBlock, "the stylesheet defines shared tokens");

  const definitions = new Set(
    [...rootBlock[1].matchAll(/(--[\w-]+)\s*:/g)].map((match) => match[1]),
  );
  for (const family of ["ink", "paper", "background", "accent", "error", "success", "border", "space-1", "space-2", "space-3", "space-4", "text-body", "text-section", "text-title", "radius"]) {
    assert.ok(definitions.has(`--${family}`), `missing shared token --${family}`);
  }

  const rules = stylesheet.slice(rootBlock.index + rootBlock[0].length);
  for (const match of rules.matchAll(/var\((--[\w-]+)\)/g)) {
    assert.ok(definitions.has(match[1]), `undefined style token ${match[1]}`);
  }
  assert.doesNotMatch(rules, /#[\da-f]{3,8}\b|\brgba?\(/i);

  for (const match of rules.matchAll(/(?:^|[;{])\s*(margin(?:-[\w-]+)?|padding(?:-[\w-]+)?|gap|font-size|border-radius)\s*:\s*([^;}]+)/gm)) {
    const valueWithoutTokens = match[2].replace(/var\(--[\w-]+\)/g, "");
    assert.doesNotMatch(valueWithoutTokens, /\b\d*\.?\d+(?:px|rem|em)\b/, `${match[1]} uses a size outside the shared tokens`);
  }
});

test("AC-44 shared text palette and interactive controls meet their stated minimums", () => {
  const stylesheet = readFileSync(join("src", "static", "css", "app.css"), "utf8");
  const rootBlock = stylesheet.match(/:root\s*\{([^}]+)\}/);
  assert.ok(rootBlock);
  const tokens = Object.fromEntries(
    [...rootBlock[1].matchAll(/(--[\w-]+)\s*:\s*(#[\da-f]{6})\s*;/gi)]
      .map((match) => [match[1], match[2]]),
  );

  const luminance = (color) => {
    const channels = color.match(/[\da-f]{2}/gi).map((channel) => {
      const value = Number.parseInt(channel, 16) / 255;
      return value <= 0.04045 ? value / 12.92 : ((value + 0.055) / 1.055) ** 2.4;
    });
    return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2];
  };
  const contrast = (foreground, background) => {
    const values = [luminance(tokens[foreground]), luminance(tokens[background])].sort((a, b) => b - a);
    return (values[0] + 0.05) / (values[1] + 0.05);
  };
  for (const [foreground, background] of [
    ["--ink", "--paper"],
    ["--accent", "--paper"],
    ["--error", "--paper"],
    ["--success", "--paper"],
    ["--paper", "--accent"],
  ]) {
    assert.ok(contrast(foreground, background) >= 4.5, `${foreground} on ${background} needs 4.5:1`);
  }
  assert.match(stylesheet, /input, textarea, button\s*\{[^}]*min-height:\s*44px/s);
  assert.match(stylesheet, /a\s*\{[^}]*min-height:\s*44px/s);
});
