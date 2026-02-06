"""
Stub scheduler to keep API runnable without APScheduler.
"""


class DataScheduler:
    def __init__(self):
        self.started = False

    def fetch_and_update(self):
        # Stubbed fetch/update
        return {"scheduled": False}

    def start(self):
        self.started = True
        print("Scheduler stub started")
        return self

    def shutdown(self):
        self.started = False
        print("Scheduler stub stopped")
