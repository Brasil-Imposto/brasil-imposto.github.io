// TypeScript types generated from the JSON Schemas in ../schemas, never written by hand (phase B0): the Python export
// validates against the same schemas, so the two sides cannot drift apart. Output: src/generated/types/ (ignored by git).
import { compileFromFile } from 'json-schema-to-typescript';
import { mkdir, readdir, writeFile } from 'node:fs/promises';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const schemas = join(here, '..', '..', 'schemas');
const out = join(here, '..', 'src', 'generated', 'types');
await mkdir(out, { recursive: true });
const names = (await readdir(schemas)).filter((f) => f.endsWith('.schema.json') && f !== 'common.schema.json').sort();
for (const f of names) {
  const ts = await compileFromFile(join(schemas, f), { cwd: schemas, bannerComment: '/* Generated from schemas/' + f + ' by scripts/gen-types.mjs. Do not edit. */', additionalProperties: false });
  await writeFile(join(out, f.replace('.schema.json', '.d.ts')), ts);
}
console.log(`${names.length} type files written`);
