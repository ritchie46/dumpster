none = ""

pytorch = """

    def save(self, f):
        import torch
        torch.save(
            {"state_dict": self.state_dict(),}, f,
        )
    
    def load(self, f):
        self.load_state_dict(state["state_dict"])
        self.eval()
"""
