none = ""

pytorch = """

    def save(self, f):
        import torch
        torch.save(
            {"state_dict": self.state_dict(),}, f,
        )
    
    def load(self, f):
        state = torch.load(f, map_location="cpu")
        self.load_state_dict(state["state_dict"])
        self.eval()
"""

pickle = """

    def save(self, f):
        import pickle
        from dumpster.kwargs import save_kwargs_state

        d = save_kwargs_state(self.__dict__)
        pickle.dump({"__dict__": d}, f)

    def load(self, f):
        import pickle
        from dumpster.kwargs import load_kwargs_state
        state = pickle.load(f)
        self.__dict__ = load_kwargs_state(state["__dict__"])
"""
