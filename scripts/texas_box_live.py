import random

class TexasBoxSimulator:
    def __init__(self):
        self.total_tickets = 10000
        self.current_ticket = 0
        self.jackpot_position = random.randint(8000, 9999)
        self.small_win_interval = 12
        self.jackpot_claimed = False
        self.near_miss_log = []

    def pull_handle(self):
        self.current_ticket += 1

        if self.current_ticket == self.jackpot_position:
            self.jackpot_claimed = True
            return "JACKPOT"

        if self.current_ticket % self.small_win_interval == 0:
            return "SMALL WIN"

        if not self.jackpot_claimed and random.random() < 0.05:
            self.near_miss_log.append(self.current_ticket)
            return "NEAR MISS"

        return "BLANK"


class TexasHeatTracker:
    def __init__(self, box_size=10000):
        self.box_size = box_size
        self.near_misses = 0
        self.small_win_gaps = []
        self.current_ticket = 0
        self.jackpot_seen = False

    def input_data(self, ticket_num, near_miss_count, gaps, jackpot_hit):
        self.current_ticket = ticket_num
        self.near_misses = near_miss_count
        self.small_win_gaps = gaps
        self.jackpot_seen = jackpot_hit

    def calculate_heat(self):
        if self.jackpot_seen:
            return 0, "DEAD - Jackpot already pulled from this batch."

        depth_pct = (self.current_ticket / self.box_size)
        depth_score = depth_pct * 40

        tease_score = min(self.near_misses * 5, 30)

        if len(self.small_win_gaps) > 2:
            import statistics
            dev = statistics.stdev(self.small_win_gaps)
            rhythm_score = max(0, 30 - (dev * 2))
        else:
            rhythm_score = 0

        total_score = depth_score + tease_score + rhythm_score

        if total_score > 75:
            rec = "HOT - Box is deep and 'Tease Code' is active."
        elif total_score > 40:
            rec = "WARM - Normal play, keep observing."
        else:
            rec = "COLD - Box is fresh or likely depleted."

        return total_score, rec


# --- Live Session ---
sim = TexasBoxSimulator()
tracker = TexasHeatTracker()

print("=== TEXAS BOX LIVE ===")
print("Box: 10,000 Tickets")
print(f"Jackpot hidden at #{sim.jackpot_position}")
print()

near_misses = 0
last_small_win = 0
small_win_gaps = []
snapshot_every = 500

for ticket in range(1, sim.total_tickets + 1):
    result = sim.pull_handle()

    if result == "JACKPOT":
        print(f"  *** TICKET #{ticket}: JACKPOT ***")
        tracker.input_data(ticket, near_misses, small_win_gaps, True)
        score, rec = tracker.calculate_heat()
        print(f"  Heat: {score:.1f}/100 | {rec}")
        print("\n=== BOX IS DEAD ===")
        break

    if result == "NEAR MISS":
        near_misses += 1

    if result == "SMALL WIN":
        if last_small_win > 0:
            small_win_gaps.append(ticket - last_small_win)
        last_small_win = ticket

    # Live heat check every 500 tickets
    if ticket % snapshot_every == 0:
        tracker.input_data(ticket, near_misses, small_win_gaps, sim.jackpot_claimed)
        score, rec = tracker.calculate_heat()
        print(f"  Ticket #{ticket:>5} | Near Misses: {near_misses:>3} | Heat: {score:>5.1f}/100 | {rec}")
