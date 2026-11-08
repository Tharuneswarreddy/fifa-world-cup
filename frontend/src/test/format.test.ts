import { describe, expect, it } from "vitest";
import { confederationName, decidedByLabel, num, scoreline, statusLabel } from "@/lib/format";

describe("format helpers", () => {
  it("formats numbers and dashes for missing values", () => {
    expect(num(1234)).toBe("1,234");
    expect(num(null)).toBe("—");
    expect(num(undefined)).toBe("—");
  });

  it("builds a scoreline and handles unrecorded scores", () => {
    expect(scoreline(3, 1)).toBe("3 : 1");
    expect(scoreline(null, 1)).toBe("– : –");
  });

  it("labels how a match was decided", () => {
    expect(decidedByLabel("penalties")).toBe("after penalties");
    expect(decidedByLabel("regulation")).toBeNull();
  });

  it("maps confederation codes to regions", () => {
    expect(confederationName("UEFA")).toBe("Europe");
    expect(confederationName(null)).toBe("—");
  });

  it("maps edition status to a tone", () => {
    expect(statusLabel("completed").tone).toBe("muted");
    expect(statusLabel("upcoming").tone).toBe("warning");
  });
});
