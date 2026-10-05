import {test} from "node:test";
import assert from "node:assert/strict";
import {enforceBudget} from "../apps/ad-studio/lib/cost-policy";
test("3元以内无需确认",()=>assert.equal(enforceBudget(2.99).requiresConfirmation,false));
test("超过3元必须确认且禁止自动降质换模型",()=>{const d=enforceBudget(3.01);assert.equal(d.requiresConfirmation,true);assert.equal(d.autoSwitchAllowed,false);assert.equal(d.qualityReductionAllowed,false);});
