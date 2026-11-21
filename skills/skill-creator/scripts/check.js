#!/usr/bin/env node
// Mechanical checks for a skill directory, using only the Node.js standard library.
//
// Usage:
//   node check.js <skill-dir>   check <skill-dir>/SKILL.md (and heading widths in references/*.md);
//                               exits 1 if any error is found
//   node check.js               run the self-check
'use strict';

const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert');

const NAME_MAX = 64;
const DESCRIPTION_MAX = 1024;
const METADATA_BUDGET = 400; // ~100 tokens at 4 chars per token, the always-loaded Level 1 budget
const BODY_LINES_MAX = 500;
const HEADING_WIDTH_MAX = 42; // display columns, about 21 full-width characters

// ponytail: counts every non-ASCII character as 2 columns, which fits Japanese headings; use a real East Asian Width table if other scripts appear
function displayWidth(text) {
  let width = 0;
  for (const ch of text) width += ch.codePointAt(0) > 0x7f ? 2 : 1;
  return width;
}

function headingWarnings(markdown, label) {
  const warnings = [];
  let inFence = false;
  for (const line of markdown.split('\n')) {
    if (/^\s*(```|~~~)/.test(line)) inFence = !inFence;
    const m = !inFence && line.match(/^#{1,6}\s+(.*?)\s*#*\s*$/);
    if (!m) continue;
    const width = displayWidth(m[1]);
    if (width > HEADING_WIDTH_MAX) warnings.push(`${label}: heading "${m[1]}" is ${width} columns wide; shorten it to about ${HEADING_WIDTH_MAX}`);
  }
  return warnings;
}

// Reads only top-level `key: value` pairs, which is all the checks need.
function parseFrontmatter(text) {
  const m = text.match(/^---\r?\n([\s\S]*?)\r?\n---(?:\r?\n|$)([\s\S]*)$/);
  if (!m) return null;
  const fields = {};
  const lines = m[1].split(/\r?\n/);
  for (let i = 0; i < lines.length; i++) {
    const kv = lines[i].match(/^([A-Za-z][\w-]*):(?:\s+(.*))?$/);
    if (!kv) continue;
    const raw = (kv[2] ?? '').trim();
    let value = raw;
    let plain = false;
    if (raw === '' || /^[>|]/.test(raw)) {
      const block = [];
      while (i + 1 < lines.length && /^\s+\S/.test(lines[i + 1])) block.push(lines[++i].trim());
      value = block.join(raw.startsWith('|') ? '\n' : ' ');
    } else if (/^(['"]).*\1$/.test(raw)) {
      value = raw.slice(1, -1);
    } else {
      plain = true;
    }
    fields[kv[1]] = { value, plain };
  }
  return { fields, body: m[2] };
}

function lint(dirName, text, exists) {
  const errors = [];
  const warnings = [];
  const fm = parseFrontmatter(text);
  if (!fm) return { errors: ['SKILL.md must start with a frontmatter block delimited by ---'], warnings };

  const name = fm.fields.name?.value ?? '';
  if (!name) {
    errors.push('name is missing');
  } else {
    if (name.length > NAME_MAX) errors.push(`name is ${name.length} chars (max ${NAME_MAX})`);
    if (!/^[a-z0-9]+(-[a-z0-9]+)*$/.test(name)) errors.push(`name "${name}" must use lowercase letters, digits, and single hyphens`);
    if (/anthropic|claude/.test(name)) errors.push(`name "${name}" must not contain "anthropic" or "claude"`);
    if (name !== dirName) errors.push(`name "${name}" does not match the directory name "${dirName}"`);
  }

  const desc = fm.fields.description;
  if (!desc || !desc.value) {
    errors.push('description is missing or empty');
  } else {
    if (desc.value.length > DESCRIPTION_MAX) errors.push(`description is ${desc.value.length} chars (max ${DESCRIPTION_MAX})`);
    if (/<\/?[A-Za-z][^>]*>/.test(desc.value)) errors.push('description must not contain XML tags');
    if (desc.plain && desc.value.includes(': ')) errors.push('description is a plain YAML scalar containing ": ", which YAML rejects; split the sentence instead');
    if (desc.plain && desc.value.includes(' #')) errors.push('description is a plain YAML scalar containing " #", which YAML reads as a comment and truncates');
    const len = `${name} ${desc.value}`.length;
    if (len > METADATA_BUDGET) warnings.push(`name + description is ${len} chars; aim for about ${METADATA_BUDGET} (~100 tokens)`);
  }

  for (const [, target] of fm.body.matchAll(/\]\(([^)\s]+)\)/g)) {
    if (/^([a-z][a-z0-9+.-]*:|#)/i.test(target)) continue;
    const file = target.split('#')[0];
    if (file.startsWith('../')) errors.push(`link "${target}" leaves the skill directory and breaks when the skill is installed alone; mention other skills by name`);
    else if (!exists(file)) errors.push(`link "${target}" points to a missing file`);
  }

  warnings.push(...headingWarnings(fm.body, 'SKILL.md'));

  const bodyLines = fm.body.split('\n').length;
  if (bodyLines > BODY_LINES_MAX) warnings.push(`body is ${bodyLines} lines; move rarely needed material to references/ (aim for under ${BODY_LINES_MAX})`);

  return { errors, warnings };
}

function selfCheck() {
  const ok = '---\nname: foo\ndescription: Do X. Use when Y.\nmetadata:\n  author: someone\n---\n# Foo\nSee [r](references/r.md) and [web](https://example.com).\n';
  const all = () => true;
  const errorsOf = (dir, text, exists = all) => lint(dir, text, exists).errors.join('\n');

  assert.strictEqual(errorsOf('foo', ok), '');
  assert.match(errorsOf('bar', ok), /does not match/);
  assert.match(errorsOf('foo', ok, () => false), /missing file/);
  assert.match(errorsOf('foo', ok.replace('[r](references/r.md)', '[c](../other/SKILL.md)')), /leaves the skill directory/);
  assert.match(errorsOf('foo', ok.replace('Do X.', 'Do X: fast.')), /": "/);
  assert.match(errorsOf('foo', ok.replace('Do X.', 'Do X #1.')), /comment/);
  assert.strictEqual(errorsOf('foo', ok.replace('Do X. Use when Y.', '"Do X: fast. Use when Y."')), '');
  assert.strictEqual(errorsOf('foo', ok.replace('Do X. Use when Y.', '>\n  Do X: fast.\n  Use when Y.')), '');
  assert.match(errorsOf('foo', ok.replace('Do X.', 'Do <b>X</b>.')), /XML/);
  assert.match(errorsOf('claude-foo', ok.replace('name: foo', 'name: claude-foo')), /must not contain/);
  assert.match(errorsOf('Foo', ok.replace('name: foo', 'name: Foo')), /lowercase/);
  assert.match(errorsOf('foo', ok.replace('description: Do X. Use when Y.\n', '')), /description is missing/);
  assert.match(errorsOf('foo', '# no frontmatter\n'), /frontmatter/);
  assert.match(lint('foo', ok.replace('Do X.', 'x'.repeat(500)), all).warnings.join(), /aim for about/);
  assert.deepStrictEqual(headingWarnings('## 会話からワークフローとユーザーの訂正を拾う\n', 'f'), []);
  assert.strictEqual(headingWarnings('## 会話からワークフローとユーザーの訂正を必ず拾う\n', 'f').length, 1);
  assert.deepStrictEqual(headingWarnings('```\n## 会話からワークフローとユーザーの訂正を必ず拾う\n```\n', 'f'), []);
}

function main() {
  const arg = process.argv[2];
  if (!arg) {
    selfCheck();
    console.log('self-check passed');
    return 0;
  }
  const skillDir = path.resolve(arg);
  const file = path.join(skillDir, 'SKILL.md');
  if (!fs.existsSync(file)) {
    console.error(`error: ${file} not found`);
    return 2;
  }
  const { errors, warnings } = lint(path.basename(skillDir), fs.readFileSync(file, 'utf8'), (p) => fs.existsSync(path.join(skillDir, p)));
  const refDir = path.join(skillDir, 'references');
  if (fs.existsSync(refDir)) {
    for (const name of fs.readdirSync(refDir).filter((n) => n.endsWith('.md')).sort()) {
      warnings.push(...headingWarnings(fs.readFileSync(path.join(refDir, name), 'utf8'), `references/${name}`));
    }
  }
  for (const e of errors) console.log(`error: ${e}`);
  for (const w of warnings) console.log(`warning: ${w}`);
  if (errors.length === 0 && warnings.length === 0) console.log(`OK ${arg}`);
  return errors.length ? 1 : 0;
}

process.exitCode = main();
