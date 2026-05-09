import random
from typing import ClassVar


class TexasBoxSimulator:
    PRIZE_TIERS: ClassVar[dict[str, int]] = {
        "JACKPOT": 500,
        "$20 WIN": 20,
        "$5 WIN": 5,
        "$2 WIN": 2,
    }

    def __init__(self, box_size=10000, ticket_cost=1, jackpot_value=500):
        self.total_tickets = box_size
        self.ticket_cost = ticket_cost
        self.current_ticket = 0

        jackpot_zone_start = int(box_size * 0.8)
        self.jackpot_position = random.randint(jackpot_zone_start, box_size - 1)  # noqa: S311

        self.small_win_interval = 12
        self.jackpot_claimed = False
        self.near_miss_log = []

        self.PRIZE_TIERS["JACKPOT"] = jackpot_value

        self.money_in = 0
        self.money_won = 0

    def pull_handle(self):
        self.current_ticket += 1
        self.money_in += self.ticket_cost

        if self.current_ticket == self.jackpot_position:
            self.jackpot_claimed = True
            self.money_won += self.PRIZE_TIERS["JACKPOT"]
            return "JACKPOT"

        if self.current_ticket % self.small_win_interval == 0:
            tier = self._pick_small_win_tier()
            self.money_won += self.PRIZE_TIERS[tier]
            return tier

        if not self.jackpot_claimed:
            distance = abs(self.current_ticket - self.jackpot_position)
            proximity = max(0, 1 - (distance / self.total_tickets))
            near_miss_chance = 0.02 + (proximity * 0.08)
            if random.random() < near_miss_chance:  # noqa: S311
                self.near_miss_log.append(self.current_ticket)
                return "NEAR MISS"

        return "BLANK"

    def _pick_small_win_tier(self):
        roll = random.random()  # noqa: S311
        if roll < 0.05:
            return "$20 WIN"
        if roll < 0.25:
            return "$5 WIN"
        return "$2 WIN"

    def roi(self):
        if self.money_in == 0:
            return 0
        return ((self.money_won - self.money_in) / self.money_in) * 100


# --- Run the Lab ---
sim = TexasBoxSimulator()
print("Simulating a 10,000 Ticket Box...")
print(
    f"Jackpot (${sim.PRIZE_TIERS['JACKPOT']}) hidden at Ticket #{sim.jackpot_position}"
)

for stage in [1000, 5000, 9000]:
    near_misses_in_stage = 0
    while sim.current_ticket < stage:
        res = sim.pull_handle()
        if res == "NEAR MISS":
            near_misses_in_stage += 1

    status = "DEAD" if sim.jackpot_claimed else "LIVE"
    print(f"\n--- Snapshot at Ticket #{stage} ---")
    print(f"Box Status: {status}")
    print(f"Near Misses spotted: {near_misses_in_stage}")
    print(
        f"Money In: ${sim.money_in} | Money Won: ${sim.money_won} | ROI: {sim.roi():.1f}%"
    )
