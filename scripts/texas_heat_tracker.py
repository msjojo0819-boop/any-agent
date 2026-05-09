import statistics


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
        if self.jackpot_seen:
            return 0, "DEAD - Jackpot already pulled from this batch."

        depth_pct = self.current_ticket / self.box_size
        depth_score = depth_pct * 40

        tease_score = min(self.near_misses * 5, 30)

        if len(self.small_win_gaps) > 2:
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


# --- Example Usage ---
tracker = TexasHeatTracker()
tracker.input_data(8500, 5, [12, 11, 13], False)
score, recommendation = tracker.calculate_heat()
print(f"Machine Heat Score: {score:.2f}/100")
print(f"Status: {recommendation}")
