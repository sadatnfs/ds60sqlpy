import { strict as assert } from 'node:assert';
import { StringDecoder } from 'node:string_decoder';

type Row = { group: string; value: number };
type Diagnostic = { line: number; code: 'json' | 'schema' };
function row(value: unknown): Row | undefined {
  if (typeof value !== 'object' || value === null || Array.isArray(value)) return undefined;
  if (Object.keys(value).sort().join(',') !== 'group,value' || !('group' in value) || !('value' in value)) return undefined;
  if (typeof value.group !== 'string' || value.group.length === 0 || value.group.length > 40 || typeof value.value !== 'number' || !Number.isSafeInteger(value.value) || Math.abs(value.value) > 1000) return undefined;
  return { group: value.group, value: value.value };
}
async function* chunks(text: string, size: number): AsyncGenerator<Uint8Array> {
  const bytes = Buffer.from(text, 'utf8');
  for (let index = 0; index < bytes.length; index += size) yield bytes.subarray(index, index + size);
}
async function* lines(source: AsyncIterable<Uint8Array>): AsyncGenerator<{ line: number; text: string }> {
  const decoder = new StringDecoder('utf8');
  let pending = '';
  let total = 0;
  let line = 0;
  for await (const chunk of source) {
    total += chunk.byteLength;
    if (total > 16384) throw new RangeError('input byte budget exceeded');
    pending += decoder.write(Buffer.from(chunk));
    let boundary: number;
    while ((boundary = pending.indexOf('\n')) >= 0) {
      const text = pending.slice(0, boundary).replace(/\r$/u, '');
      pending = pending.slice(boundary + 1);
      if (Buffer.byteLength(text) > 1024) throw new RangeError('line byte budget exceeded');
      yield { line: ++line, text };
    }
    if (Buffer.byteLength(pending) > 1024) throw new RangeError('line byte budget exceeded');
  }
  pending += decoder.end();
  if (pending !== '') yield { line: ++line, text: pending.replace(/\r$/u, '') };
}
async function analyze(source: AsyncIterable<Uint8Array>): Promise<{ groups: Map<string, { count: number; sum: number }>; accepted: number; rejected: Diagnostic[] }> {
  const groups = new Map<string, { count: number; sum: number }>();
  const rejected: Diagnostic[] = [];
  let accepted = 0;
  for await (const entry of lines(source)) {
    if (entry.text.trim() === '') continue;
    let value: unknown;
    try { value = JSON.parse(entry.text); }
    catch { rejected.push({ line: entry.line, code: 'json' }); continue; }
    const parsed = row(value);
    if (!parsed) { rejected.push({ line: entry.line, code: 'schema' }); continue; }
    const previous = groups.get(parsed.group) ?? { count: 0, sum: 0 };
    groups.set(parsed.group, { count: previous.count + 1, sum: previous.sum + parsed.value });
    accepted += 1;
  }
  return { groups, accepted, rejected };
}

export async function verify(): Promise<{ checks: number; status: string }> {
  // Exercise 1: Aggregate valid split-byte input
  {
    const text = [{ group: 'A', value: 2 }, { group: 'B', value: 4 }, { group: 'A', value: 3 }].map(row => JSON.stringify(row)).join('\n');
    const result = await analyze(chunks(text, 3));
    assert.deepEqual([...result.groups], [['A', { count: 2, sum: 5 }], ['B', { count: 1, sum: 4 }]]);
    assert.equal(result.accepted, 3);
    assert.deepEqual(result.rejected, []);
  }

  // Exercise 2: Quarantine syntax and domain failures with physical line numbers
  {
    const text = '{"group":"A","value":2}\n{broken\n{"group":"A","value":"wrong"}\n';
    const result = await analyze(chunks(text, 2));
    assert.equal(result.accepted, 1);
    assert.deepEqual(result.rejected, [{ line: 2, code: 'json' }, { line: 3, code: 'schema' }]);
    assert.deepEqual(result.groups.get('A'), { count: 1, sum: 2 });
  }

  // Exercise 3: Preserve a multi-byte group name across single-byte chunks
  {
    const result = await analyze(chunks(JSON.stringify({ group: '😀', value: 7 }), 1));
    assert.deepEqual(result.groups.get('😀'), { count: 1, sum: 7 });
    assert.equal(result.rejected.length, 0);
  }

  // Exercise 4: Handle blank lines and a final line without newline
  {
    const text = '\n{"group":"A","value":1}\r\n\n{"group":"A","value":2}';
    const result = await analyze(chunks(text, 4));
    assert.equal(result.accepted, 2);
    assert.deepEqual(result.groups.get('A'), { count: 2, sum: 3 });
    assert.deepEqual(result.rejected, []);
  }

  // Exercise 5: Enforce input and record budgets
  {
    await assert.rejects(analyze(chunks('x'.repeat(1025), 10)), RangeError);
    await assert.rejects(analyze(chunks('\n'.repeat(16385), 1000)), RangeError);
  }

  // Exercise 6: Expose incomplete-data counts and empty input
  {
    const invalid = await analyze(chunks('{"group":"A","value":null}', 5));
    const empty = await analyze(chunks('', 5));
    assert.equal(invalid.accepted, 0);
    assert.equal(invalid.rejected.length, 1);
    assert.equal(empty.accepted, 0);
    assert.equal(empty.rejected.length, 0);
    assert.equal(empty.groups.size, 0);
  }

  return { checks: 6, status: "passed" };
}

console.log(JSON.stringify(await verify()));
