from pyswip import Prolog
from gui import CheckButtonState
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

    def receive_query(self, operator: CheckButtonState, word_1: str, word_2: str):
        """Receive two words and the operator to apply, and set the query"""

        self.operator = operator
        self.word_1 = WordInfo(word_1)
        self.word_2 = WordInfo(word_2)

    def process_query(self):
        """Perform the operation in the query"""

        self.result_string = "Processing..."

        # Check for the Assertion operator.
        if self.operator == CheckButtonState.ASSERTION:
            self.result_string = self.assertion()

    def assertion(self):
        """Search all possible meanings of the word 1"""

        # Get the principal data of the word 1
        self.fill_word_info(1)

        if not self.word_1.exist:
            return self.not_found(self.word_1.word)

        # Get all the word info through the g predicate.
        for synset_id in self.word_1.synset_id_list:
            g_result = self.make_consult(f"g({synset_id}, Gloss)")
            self.word_1.gloss_list.append(g_result[0]["Gloss"])

        # Create the result string.
        result_string = ""
        for i in range(len(self.word_1.synset_id_list)):
            result_string += f"{self.word_1.word}:\n  ({self.word_1.word_type_list[i]}):\n    {self.word_1.gloss_list[i]}\n"

        return result_string

    def fill_word_info(self, word_selector: int):
        temp_word = self.word_1 if word_selector == 1 else self.word_2

        # Get all the word info through the s predicate.
        s_result = self.make_consult(
            f"s(SynsetID, WordNumber,'{temp_word.word}', WordType, WordSense, TagCount)"
        )

        # Check if the word exists.
        temp_word.exist = s_result != []

        # Fill the word info with the results.
        for result in s_result:
            temp_word.synset_id_list.append(result["SynsetID"])
            temp_word.word_number_list.append(result["WordNumber"])
            temp_word.word_sense_list.append(result["WordSense"])
            temp_word.word_type_list.append(
                self.translate_word_type(result["WordType"])
            )
            temp_word.tag_count_list.append(result["TagCount"])

    def make_consult(self, query: str) -> list:
        """Make a consult to the prolog file."""
        return list(self.prolog.query(query))

    def translate_word_type(self, word_type: str) -> str:
        """Translate the word type to a more readable format."""
        if word_type == "n":
            return "noun"
        elif word_type == "v":
            return "verb"
        elif word_type == "a" or word_type == "s":
            return "adjective"
        elif word_type == "r":
            return "adverb"
        else:
            return "unknown"

    def not_found(self, word):
        return f"The word {word} was not found in the database."


class WordInfo:
    """Class that contains the information of a word."""

    def __init__(self, word: str):
        self.word = word
        self.synset_id_list = []
        self.word_type_list = []
        self.word_number_list = []
        self.word_sense_list = []
        self.gloss_list = []
        self.tag_count_list = []
        self.exist = False

    def __str__(self):
        return self.word
