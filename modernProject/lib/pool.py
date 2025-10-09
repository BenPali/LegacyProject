class Pool:
    def __init__(self, max_workers=10):
        self.max_workers = max_workers
        self.workers = []
    
    def submit(self, fn, *args, **kwargs):
        result = fn(*args, **kwargs)
        return result
    
    def shutdown(self):
        self.workers = []
