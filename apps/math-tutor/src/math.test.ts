import { describe, expect, it } from "vitest";
import { addWholeNumbers } from "./math";

describe("addWholeNumbers", () => {
  it("adds non-negative whole numbers", () => {
    expect(addWholeNumbers(17, 25)).toBe(42);
  });

  it("rejects non-integer input rather than silently rounding", () => {
    expect(() => addWholeNumbers(1.5, 2)).toThrow(TypeError);
  });
});
