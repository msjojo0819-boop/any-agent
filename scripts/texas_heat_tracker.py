class TexasHeatTracker:
    def __init__(self, box_size=10000):
        self.box_size = box_size
        self.near_misses = 0
        self.small_win_gaps = []
        self.current_ticket = 0
        self.jackpot_seen = False

    def input_data(self, ticket_num, near_miss_count, gaps, jackpot_hit_in_room):
        self.current_ticket = ticket_num
        self.near_misses = near_miss_count
        self.small_win_gaps = gaps
        self.jackpot_seen = jackpot_hit_in_room

    def calculate_heat(self):
        # 1. Check for 'Dead Box' Condition
        if self.jackpot_seen:
            return 0, "DEAD - Jackpot already pulled from this batch."

        # 2. Calculate Depth Score (0-40 points)
        # Closer to the end of the box is better
        depth_pct = (self.current_ticket / self.box_size)
        depth_score = depth_pct * 40

        # 3. Calculate Tease Score (0-30 points)
        # High frequency of near-misses indicates the Jackpot is still 'Live'
        tease_score = min(self.near_misses * 5, 30)

        # 4. Calculate Rhythm Score (0-30 points)
        # Low standard deviation in gaps means a 'Lazy' predictable shuffle
        if len(self.small_win_gaps) > 2:
            import statistics
            dev = statistics.stdev(self.small_win_gaps)
            # If variation is low, the rhythm is high
            rhythm_score = max(0, 30 - (dev * 2))
        else:
            rhythm_score = 0

        total_score = depth_score + tease_score + rhythm_score

        # Final Recommendation
        if total_score > 75:
            rec = "HOT - Box is deep and 'Tease Code' is active."
        elif total_score > 40:
            rec = "WARM - Normal play, keep observing."
        else:
            rec = "COLD - Box is fresh or likely depleted."

        return total_score, rec

# --- Example Usage ---
tracker = TexasHeatTracker()
# Observation: Ticket #8500, 5 Near Misses seen, Gaps were 12, 11, 13
tracker.input_data(8500, 5, [12, 11, 13], False)
score, recommendation = tracker.calculate_heat()
print(f"Machine Heat Score: {score:.2f}/100")
print(f"Status: {recommendation}")
