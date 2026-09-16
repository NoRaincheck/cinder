#!/usr/bin/env node
/**
 * Patch Chapbook 2.x engine to fix [continue] modifier not resetting conditionEval.
 *
 * Bug: The [continue] modifier's process() function is empty, so conditionEval
 * (set by [if]/[else] modifiers) bleeds into subsequent blocks within the same
 * passage. This causes text after [continue] to be incorrectly cleared when a
 * preceding [if] condition evaluated to false.
 *
 * Fix: Make [continue]'s process() reset conditionEval to undefined.
 *
 * Original:  process(){}}
 * Patched:   process(n,c){c.state.conditionEval=void 0}}
 *
 * See: https://klembot.github.io/chapbook/guide/en/state/conditions-and-variables.html
 */

const fs = require("fs");
const path = require("path");

const distPath = path.join(__dirname, "..", "dist", "index.html");

if (!fs.existsSync(distPath)) {
  console.error("dist/index.html not found. Run `just build` first.");
  process.exit(1);
}

let html = fs.readFileSync(distPath, "utf-8");

const before = "process(){}}";
const after = "process(n,c){c.state.conditionEval=void 0}}";

// Repair a dist previously patched with the broken single-arg form
// process(c){c.state...} (first arg is the block, not the context).
const broken = "process(c){c.state.conditionEval=void 0}}";
const brokenCount = (html.match(new RegExp(broken.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"), "g")) || []).length;
if (brokenCount > 0) {
  html = html.replace(broken, after);
  fs.writeFileSync(distPath, html, "utf-8");
  console.log(`Repaired ${brokenCount} occurrence(s) of broken [continue] patch in dist/index.html`);
  console.log("  Before: process(c){c.state.conditionEval=void 0}}");
  console.log("  After:  process(n,c){c.state.conditionEval=void 0}}");
  process.exit(0);
}

const count = (html.match(new RegExp(before.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"), "g")) || []).length;

if (count === 0) {
  console.log("No patches needed (pattern not found).");
  process.exit(0);
}

if (count !== 1) {
  console.error(`WARNING: Found ${count} occurrences of pattern (expected 1).`);
}

html = html.replace(before, after);
fs.writeFileSync(distPath, html, "utf-8");

console.log(`Patched ${count} occurrence(s) of [continue] modifier in dist/index.html`);
console.log("  Before: process(){}}");
console.log("  After:  process(n,c){c.state.conditionEval=void 0}}");
