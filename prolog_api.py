from pyswip import Prolog
import os


class Consulter:
    def __init__(self):
        # Create the prolog object.
        self.prolog = Prolog()

        # Consult the prolog files.
        self.load_consults()

    def load_consults(self):
        """Load every prolog file in prolog_files."""

        for file in os.listdir("prolog_files"):
            if file.endswith(".pl"):
                self.prolog.consult("prolog_files/" + file)
