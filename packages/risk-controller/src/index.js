export const LEVELS = Object.freeze({
  READ_ONLY: 'LEVEL_1_READ_ONLY',
  APPROVAL_REQUIRED: 'LEVEL_2_APPROVAL_REQUIRED',
  AUTO_EXECUTION: 'LEVEL_3_AUTO_EXECUTION'
});

const WRITE_TOOLS = new Set([
  'set_budget', 'set_bid', 'pause_campaign', 'resume_campaign',
  'set_keyword_bid', 'set_targeting'
]);

export function checkAction({ tool, permission = LEVELS.READ_ONLY, approved = false }) {
  if (!WRITE_TOOLS.has(tool)) return { allowed: true, reason: 'read_operation' };
  if (permission === LEVELS.READ_ONLY) return { allowed: false, reason: 'read_only_mode' };
  if (permission === LEVELS.APPROVAL_REQUIRED && !approved) return { allowed: false, reason: 'approval_required' };
  return { allowed: permission === LEVELS.AUTO_EXECUTION || approved, reason: 'passed' };
}
