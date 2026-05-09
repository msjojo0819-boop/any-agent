import random
import statistics
from typing import ClassVar

# --- Configuration ---
BOX_SIZE = 10000
TICKET_COST = 1
JACKPOT_VALUE = 500
SNAPSHOT_EVERY = 500
MULTI_BOX_RUNS = 100


class TexasBoxSimulator:
    PRIZE_TIERS: ClassVar[dict[str, int]] = {
        "$20 WIN": 20,
        "$5 WIN": 5,
        "$2 WIN": 2,
    }

    def __init__(
        self, box_size=BOX_SIZE, ticket_cost=TICKET_COST, jackpot_value=JACKPOT_VALUE
    ):
        self.total_tickets = box_size
        self.ticket_cost = ticket_cost
        self.jackpot_value = jackpot_value
        self.current_ticket = 0

        jackpot_zone_start = int(box_size * 0.8)
        self.jackpot_position = random.randint(jackpot_zone_start, box_size - 1)  # noqa: S311

        self.small_win_interval = 12
        self.jackpot_claimed = False
        self.near_miss_log = []

        self.money_in = 0
        self.money_won = 0

    def pull_handle(self):
        self.current_ticket += 1
        self.money_in += self.ticket_cost

        if self.current_ticket == self.jackpot_position:
            self.jackpot_claimed = True
            self.money_won += self.jackpot_value
            return "JACKPOT"

        if self.current_ticket % self.small_win_interval == 0:
            tier, payout = self._pick_small_win_tier()
            self.money_won += payout
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
            return "$20 WIN", 20
        if roll < 0.25:
            return "$5 WIN", 5
        return "$2 WIN", 2

    def roi(self):
        if self.money_in == 0:
            return 0.0
        return ((self.money_won - self.money_in) / self.money_in) * 100


class TexasHeatTracker:
    def __init__(self, box_size=BOX_SIZE):
        self.box_size = box_size
        self.near_misses = 0
        self.small_win_gaps = []
        self.current_ticket = 0
        self.jackpot_seen = False

    def input_data(self, ticket_num, near_miss_count, gaps, jackpot_hit):
        self.current_ticket = ticket_num
        self.near_misses = near_miss_count
        self.small_win_gaps = list(gaps)
        self.jackpot_seen = jackpot_hit

    def calculate_heat(self):
        if self.jackpot_seen:
            return 0.0, "DEAD"

        depth_score = (self.current_ticket / self.box_size) * 40
        tease_score = min(self.near_misses * 5, 30)

        if len(self.small_win_gaps) > 2:
            dev = statistics.stdev(self.small_win_gaps)
            rhythm_score = max(0, 30 - (dev * 2))
        else:
            rhythm_score = 0.0

        total_score = depth_score + tease_score + rhythm_score

        if total_score > 75:
            rec = "HOT"
        elif total_score > 40:
            rec = "WARM"
        else:
            rec = "COLD"

        return total_score, rec


def run_single_box(
    box_size=BOX_SIZE,
    ticket_cost=TICKET_COST,
    jackpot_value=JACKPOT_VALUE,
    verbose=True,
):
    sim = TexasBoxSimulator(box_size, ticket_cost, jackpot_value)
    tracker = TexasHeatTracker(box_size)

    if verbose:
        print("=" * 65)
        print(
            f"  TEXAS BOX LIVE  |  {box_size:,} Tickets  |  ${ticket_cost}/pull  |  Jackpot: ${jackpot_value}"
        )
        print(f"  Jackpot hidden at Ticket #{sim.jackpot_position}")
        print("=" * 65)

    near_misses = 0
    last_small_win = 0
    small_win_gaps = []
    wins_by_tier = {"$2 WIN": 0, "$5 WIN": 0, "$20 WIN": 0, "JACKPOT": 0}

    for ticket in range(1, sim.total_tickets + 1):
        result = sim.pull_handle()

        if result in wins_by_tier:
            wins_by_tier[result] += 1

        if result == "JACKPOT":
            if verbose:
                print(f"\n  *** TICKET #{ticket}: JACKPOT ${jackpot_value}! ***")
                print(
                    f"  Money In: ${sim.money_in} | Money Won: ${sim.money_won} | ROI: {sim.roi():.1f}%"
                )
                print("  === BOX IS DEAD ===")
            break

        if result == "NEAR MISS":
            near_misses += 1

        if result in ("$2 WIN", "$5 WIN", "$20 WIN"):
            if last_small_win > 0:
                small_win_gaps.append(ticket - last_small_win)
            last_small_win = ticket

        if verbose and ticket % SNAPSHOT_EVERY == 0:
            tracker.input_data(ticket, near_misses, small_win_gaps, sim.jackpot_claimed)
            score, rec = tracker.calculate_heat()
            print(
                f"  #{ticket:>5} | "
                f"NM: {near_misses:>3} | "
                f"Heat: {score:>5.1f} [{rec:>4}] | "
                f"${sim.money_won:>5} won / ${sim.money_in:>5} in ({sim.roi():>+6.1f}%)"
            )

    return {
        "jackpot_ticket": sim.jackpot_position,
        "money_in": sim.money_in,
        "money_won": sim.money_won,
        "roi": sim.roi(),
        "near_misses": near_misses,
        "wins": wins_by_tier,
        "jackpot_claimed": sim.jackpot_claimed,
    }


def run_multi_box(
    num_boxes=MULTI_BOX_RUNS,
    box_size=BOX_SIZE,
    ticket_cost=TICKET_COST,
    jackpot_value=JACKPOT_VALUE,
):
    print("\n" + "=" * 65)
    print(f"  MULTI-BOX ANALYSIS  |  {num_boxes} Boxes  |  {box_size:,} Tickets Each")
    print("=" * 65)

    results = []
    for _ in range(num_boxes):
        res = run_single_box(box_size, ticket_cost, jackpot_value, verbose=False)
        results.append(res)

    rois = [r["roi"] for r in results]
    total_in = sum(r["money_in"] for r in results)
    total_won = sum(r["money_won"] for r in results)
    total_near_misses = sum(r["near_misses"] for r in results)
    jackpots_hit = sum(1 for r in results if r["jackpot_claimed"])

    hot_correct = 0
    hot_total = 0
    for r in results:
        tracker = TexasHeatTracker(box_size)
        check_at = int(box_size * 0.75)
        tracker.input_data(check_at, r["near_misses"], [12, 12, 12], False)
        _score, rec = tracker.calculate_heat()
        if rec == "HOT":
            hot_total += 1
            if r["jackpot_claimed"] and r["jackpot_ticket"] > check_at:
                hot_correct += 1

    print(f"\n  Boxes Run:        {num_boxes}")
    print(
        f"  Jackpots Hit:     {jackpots_hit}/{num_boxes} ({jackpots_hit / num_boxes * 100:.1f}%)"
    )
    print(f"  Total Money In:   ${total_in:,}")
    print(f"  Total Money Won:  ${total_won:,}")
    print(f"  Overall ROI:      {((total_won - total_in) / total_in) * 100:+.1f}%")
    print(f"  Avg ROI per Box:  {statistics.mean(rois):+.1f}%")
    print(f"  Best ROI:         {max(rois):+.1f}%")
    print(f"  Worst ROI:        {min(rois):+.1f}%")
    print(f"  Avg Near Misses:  {total_near_misses / num_boxes:.0f}")
    if hot_total > 0:
        print(
            f"\n  Heat Predictor:   {hot_correct}/{hot_total} HOT calls had jackpot remaining ({hot_correct / hot_total * 100:.0f}% accurate)"
        )
    else:
        print("\n  Heat Predictor:   No HOT signals generated")


# --- Main ---
if __name__ == "__main__":
    print("\n>>> SINGLE BOX RUN <<<")
    run_single_box()

    print("\n\n>>> MULTI-BOX ANALYSIS <<<")
    run_multi_box()
