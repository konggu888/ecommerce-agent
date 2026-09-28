import test from 'node:test';
import assert from 'node:assert/strict';
import { checkAction, LEVELS } from '../packages/risk-controller/src/index.js';

test('read operations are allowed', () => {
  assert.deepEqual(checkAction({ tool: 'get_campaigns' }), { allowed: true, reason: 'read_operation' });
});

test('write operations are blocked by default', () => {
  assert.deepEqual(checkAction({ tool: 'set_budget' }), { allowed: false, reason: 'read_only_mode' });
});

test('approval mode requires approval', () => {
  assert.equal(checkAction({ tool: 'set_bid', permission: LEVELS.APPROVAL_REQUIRED }).allowed, false);
  assert.equal(checkAction({ tool: 'set_bid', permission: LEVELS.APPROVAL_REQUIRED, approved: true }).allowed, true);
});
