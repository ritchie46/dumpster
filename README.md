# Dumpster

Utility that dumps your **model state**, the **source code** and the **global imports**. This ensures that dumped
models can be loaded even when the class definition in your project has changed or has ceased to exist.

**Currently supported**:
 * file storage
 * google cloud storage
 
 
## Installation

Development version

`pip install git+https://github.com/ritchie46/dumpster.git`

(Future) stable version

`pip install dumpster`
 
 ## Usage
 ```python
from dumpster.registries.file import ModelRegistry
import torch
from torch import nn


class PytorchModel(nn.Module):
    def __init__(self, input_size):
        super().__init__()
        self.layer = nn.Linear(input_size, 1)
    
    def forward(self, x):
        return self.layer(x)
        
    def save(self):
        return self.state_dict()
    
    def load(self, state):
        self.load_state_dict(state)
        

mr = ModelRegistry('model')

# Registering the model class inspects the source code 
# initializes object.
mr.register(PytorchModel, input_size=10)

# Model instance is available under .model_ attribute
y = mr.model_(torch.ones(10))

# Save model to file
mr.dump('save-directory')

# Load model
mr.load('save-directory')
```