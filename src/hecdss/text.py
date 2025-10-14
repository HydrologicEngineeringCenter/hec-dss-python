
class Text:
    def __init__(self):
        """
        Initialize a Text object with default values.
        """
        self.id = None
        self.text = ""

    @staticmethod
    def create(id:str, text:str):
        """
        Create a Text object with the provided text.

        Parameters:
        text (str): The text data.
        """
        txt = Text()
        txt.id = id
        txt.text = text

        return txt
