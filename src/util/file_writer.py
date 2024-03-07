import os


class FileWriter:
    """
    A class for writing text to a file, creating the file and directory if they don't exist.
    """

    @staticmethod
    def write_text_to_file(file_path: str, text: str) -> None:
        """
        Write text to the specified file path.

        This method creates the file if it doesn't exist and also creates the path to the file
        if it doesn't exist either.

        Args:
            file_path (str): The path to the file to be written.
            text (str): The text to be written to the file.
        """
        # Create the directory if it doesn't exist
        directory = os.path.dirname(file_path)
        if not os.path.exists(directory):
            os.makedirs(directory)

        # Write the text to the file
        with open(file_path, 'w') as file:
            file.write(text)
