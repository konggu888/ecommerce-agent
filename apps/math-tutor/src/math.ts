/** Small deterministic helper used only to prove the front-end test pipeline. */
export function addWholeNumbers(left: number, right: number): number {
  if (!Number.isSafeInteger(left) || !Number.isSafeInteger(right)) {
    throw new TypeError("Expected safe whole numbers");
  }
  const result = left + right;
  if (!Number.isSafeInteger(result)) throw new RangeError("Result exceeds safe integer range");
  return result;
}
