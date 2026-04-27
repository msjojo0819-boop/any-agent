import random


class TexasBoxSimulator:
    def __init__(self):
        self.total_tickets = 10000
        self.current_ticket = 0
        # We 'Back-Load' the jackpot into the last 20% of the box
        self.jackpot_position = random.randint(8000, 9999)
        # Small wins are spread out every 10-15 tickets (Lazy Symmetrical Shuffle)
        self.small_win_interval = 12

        self.jackpot_claimed = False
        self.near_miss_log = []

    def pull_handle(self):
        self.current_ticket += 1

        # 1. Check for Jackpot
        if self.current_ticket == self.jackpot_position:
            self.jackpot_claimed = True
            return "JACKPOT"

        # 2. Check for Small Win (Symmetrical Pattern)
        if self.current_ticket % self.small_win_interval == 0:
            return "SMALL WIN"

        # 3. Check for 'Near Miss' (The Tease)
        # Logic: Only tease if the jackpot is still in the box
        if not self.jackpot_claimed and random.random() < 0.05:
            self.near_miss_log.append(self.current_ticket)
            return "NEAR MISS"

        return "BLANK"


# --- Run the Lab ---
sim = TexasBoxSimulator()
print("Simulating a 10,000 Ticket Box...")
print(f"Target Jackpot is hidden at Ticket #{sim.jackpot_position}")

# We will 'Snapshot' the machine at three stages: Start, Middle, and End
for stage in [1000, 5000, 9000]:
    near_misses_in_stage = 0
    while sim.current_ticket < stage:
        res = sim.pull_handle()
        if res == "NEAR MISS":
            near_misses_in_stage += 1

    status = "DEAD" if sim.jackpot_claimed else "LIVE"
    print(f"\n--- Snapshot at Ticket #{stage} ---")
    print(f"Box Status: {status}")
    print(f"Near Misses spotted in this window: {near_misses_in_stage}")
