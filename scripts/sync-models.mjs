#!/usr/bin/env node
import { readFileSync, writeFileSync, readdirSync, existsSync } from "node:fs";
import { basename, join } from "node:path";

const repoRoot = process.cwd();
const targetSettingsPath = join(repoRoot, ".execflow", "settings.yml");
const packageSettingsPath = join(repoRoot, "execflow", "settings.yml");
const settingsPath = existsSync(targetSettingsPath) ? targetSettingsPath : packageSettingsPath;
const projectPromptDir = join(repoRoot, ".pi", "prompts");
const packagePromptDir = join(repoRoot, "prompts");

function fail(message) {
  process.stderr.write(`${message}\n`);
  process.exit(1);
}

function stripInlineComment(line) {
  const hashIndex = line.indexOf("#");
  if (hashIndex === -1) return line;
  return line.slice(0, hashIndex);
}

function parseSimpleScalar(raw, anchors) {
  const value = raw.trim();
  if (!value) return "";

  if (value.startsWith("*")) {
    const aliasName = value.slice(1).trim();
    if (!anchors.has(aliasName)) {
      fail(`Unknown YAML alias *${aliasName}`);
    }
    return anchors.get(aliasName);
  }

  if ((value.startsWith('"') && value.endsWith('"')) || (value.startsWith("'") && value.endsWith("'"))) {
    return value.slice(1, -1);
  }

  return value;
}

function parseScalarWithAnchor(raw, anchors, lineForErrors) {
  const trimmed = raw.trim();
  if (!trimmed) return "";

  const anchorMatch = trimmed.match(/^&([A-Za-z0-9_-]+)\s+(.*)$/);
  let anchorName = null;
  let valueText = trimmed;

  if (anchorMatch) {
    anchorName = anchorMatch[1];
    valueText = anchorMatch[2].trim();
    if (!valueText) {
      fail(`Empty anchored value in settings.yml: ${lineForErrors}`);
    }
  }

  const value = parseSimpleScalar(valueText, anchors);
  if (anchorName) {
    anchors.set(anchorName, value);
  }
  return value;
}

function parseSimpleYaml(text) {
  const root = {};
  const anchors = new Map();
  const stack = [{ indent: -1, obj: root }];

  for (const originalLine of text.replace(/\r/g, "").split("\n")) {
    const line = stripInlineComment(originalLine).replace(/\s+$/, "");
    if (!line.trim()) continue;

    const indentMatch = line.match(/^\s*/);
    const indent = indentMatch ? indentMatch[0].length : 0;
    if (indent % 2 !== 0) {
      fail(`Unsupported indentation in settings.yml: ${originalLine}`);
    }

    while (stack.length > 1 && indent <= stack[stack.length - 1].indent) {
      stack.pop();
    }

    const parent = stack[stack.length - 1].obj;
    const content = line.slice(indent);
    const match = content.match(/^([A-Za-z0-9_.-]+):(?:\s*(.*))?$/);
    if (!match) {
      fail(`Unsupported settings.yml line: ${originalLine}`);
    }

    const [, key, rawValue = ""] = match;
    if (rawValue.trim() === "") {
      const child = {};
      parent[key] = child;
      stack.push({ indent, obj: child });
      continue;
    }

    parent[key] = parseScalarWithAnchor(rawValue, anchors, originalLine);
  }

  return root;
}

function extractFrontmatter(text, filePath) {
  const match = text.match(/^(---\n)([\s\S]*?)(\n---\n?)([\s\S]*)$/);
  if (!match) {
    fail(`Missing markdown frontmatter in ${filePath}`);
  }
  return {
    prefix: match[1],
    frontmatter: match[2],
    separator: match[3],
    body: match[4],
  };
}

function frontmatterHasField(lines, key) {
  return lines.some((line) => new RegExp(`^${key}:\\s*`).test(line));
}

function upsertFrontmatterField(lines, key, value) {
  const rendered = `${key}: ${value}`;
  const index = lines.findIndex((line) => line.match(new RegExp(`^${key}:\\s*`)));
  if (index !== -1) {
    lines[index] = rendered;
    return;
  }

  if (key === "model") {
    const anchor = lines.findIndex((line) => /^argument-hint:\s*/.test(line));
    if (anchor !== -1) {
      lines.splice(anchor + 1, 0, rendered);
      return;
    }
    const description = lines.findIndex((line) => /^description:\s*/.test(line));
    if (description !== -1) {
      lines.splice(description + 1, 0, rendered);
      return;
    }
  }

  if (key === "thinking") {
    const modelIndex = lines.findIndex((line) => /^model:\s*/.test(line));
    if (modelIndex !== -1) {
      lines.splice(modelIndex + 1, 0, rendered);
      return;
    }
  }

  lines.push(rendered);
}

function resolvePromptConfig(promptKey, settings) {
  const prompts = settings.prompts ?? {};
  return prompts[promptKey] ?? prompts[`${promptKey}.md`] ?? null;
}

function syncPromptFile(filePath, settings) {
  const promptKey = basename(filePath, ".md");
  const text = readFileSync(filePath, "utf8");
  const { prefix, frontmatter, separator, body } = extractFrontmatter(text, filePath);
  const lines = frontmatter.split("\n");
  const promptConfig = resolvePromptConfig(promptKey, settings);

  if (!promptConfig) {
    if (frontmatterHasField(lines, "model") || frontmatterHasField(lines, "thinking")) {
      fail(`Missing prompts.${promptKey} in ${settingsPath}`);
    }
    return {
      file: filePath,
      source: "skipped",
      model: null,
      thinking: null,
      changed: false,
      skipped: true,
    };
  }

  if (promptConfig.model === undefined || promptConfig.model === "") {
    fail(`Missing prompts.${promptKey}.model in ${settingsPath}`);
  }
  if (promptConfig.thinking === undefined || promptConfig.thinking === "") {
    fail(`Missing prompts.${promptKey}.thinking in ${settingsPath}`);
  }

  upsertFrontmatterField(lines, "model", promptConfig.model);
  upsertFrontmatterField(lines, "thinking", promptConfig.thinking);

  const updated = `${prefix}${lines.join("\n")}${separator}${body}`;
  const changed = updated !== text;
  if (changed) {
    writeFileSync(filePath, updated);
  }

  return {
    file: filePath,
    source: `prompts.${promptKey}`,
    model: promptConfig.model,
    thinking: promptConfig.thinking,
    changed,
    skipped: false,
  };
}

if (!existsSync(settingsPath)) {
  fail(`Missing ${settingsPath}. Run /init-execflow first or create the settings file.`);
}

const promptDir = existsSync(targetSettingsPath)
  ? projectPromptDir
  : packagePromptDir;

if (!existsSync(promptDir)) {
  if (existsSync(targetSettingsPath)) {
    fail(`Missing ${promptDir}. Run /init-execflow first to scaffold .pi/prompts/.`);
  }
  fail(`Missing ${promptDir}. Nothing to sync.`);
}

const settings = parseSimpleYaml(readFileSync(settingsPath, "utf8"));
const promptFiles = readdirSync(promptDir).filter((name) => name.endsWith(".md")).sort();
const results = promptFiles.map((promptFile) => syncPromptFile(join(promptDir, promptFile), settings));

const changed = results.filter((result) => result.changed);
const skipped = results.filter((result) => result.skipped);
const relativeSettingsPath = settingsPath.replace(`${repoRoot}/`, "");
process.stdout.write(`Applied model settings from ${relativeSettingsPath}\n`);
process.stdout.write(`Updated ${changed.length} of ${results.length - skipped.length} configured prompt files.\n`);
for (const result of results) {
  const relativePath = result.file.replace(`${repoRoot}/`, "");
  if (result.skipped) {
    process.stdout.write(`- ${relativePath}: skipped | no prompt config and no model frontmatter\n`);
    continue;
  }
  const state = result.changed ? "updated" : "unchanged";
  const thinkingSuffix = result.thinking ? ` | thinking=${result.thinking}` : "";
  process.stdout.write(`- ${relativePath}: ${state} | source=${result.source} | model=${result.model}${thinkingSuffix}\n`);
}
