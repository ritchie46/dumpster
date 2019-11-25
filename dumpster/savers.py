

pytorch = """

    def save(self, f):
        import torch
        torch.save(
            {"state_dict": self.state_dict(),}, f,
        )
"""