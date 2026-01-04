from .config.config import ConfigTemplate
from . import __version__

class MeslyApp:
    def __init__(self):
        print("MeslyApp v%s" % __version__)
        print("Initializing Mesly...")
        self.config = ConfigTemplate.get_config()
