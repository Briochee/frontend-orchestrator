import test from 'node:test';
import assert from 'node:assert/strict';
import {orders,money} from '../src/data.js';
test('sample order fixture exists',()=>assert.ok(orders.length>=5));
test('USD formatting is stable',()=>assert.equal(money(12.5),'$12.50'));
// Intentionally insufficient interaction, visual, security and accessibility coverage.
