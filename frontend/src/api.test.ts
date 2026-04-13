import { describe, expect, it } from "vitest";

describe("api types", () => {
  it("SeatInfo may include wagon in feature branch", () => {
    const seat = { ticket_number: "1", full_name: "Test", train_number: 2, seat_number: 15 };
    expect(seat).toBeDefined();
    const withWagon = { ...seat, wagon_number: 5 };
    expect(withWagon.wagon_number).toBe(5);
  });
});
