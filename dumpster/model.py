from distutils import config
import pickle


class ExampleModel:
    def __init__(self, param):
        # run a global import
        self.a = config.Command
        self.param = param

    def save(self, file):
        pickle.dump(self.a, file)

    def load(self, state):
        self.a = pickle.load(state)
