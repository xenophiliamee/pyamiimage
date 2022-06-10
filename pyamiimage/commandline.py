import argparse
import sys

from pyamiimage.ami_ocr import AmiOCR


class Pyamiimage:
    """[summary]"""

    def __init__(self) -> None:
        self.version = "0.0.7"



    def execute(self, args):
        if args.text:
            ocr = AmiOCR(args.infile.name)
            textboxes = ocr.get_textboxes()
            AmiOCR.write_text_to_file(textboxes, args.outfile.name)

    def handlecli(self):
        """Handles the command line interface using argpase"""
        parser = argparse.ArgumentParser(description="Welcome to pyamiimage, view --help")
        parser.add_argument(
            'infile', 
            nargs='?', 
            type=argparse.FileType('r'),
            default=sys.stdin
            )
        parser.add_argument(
            'outfile',
            nargs='?',
            type=argparse.FileType('w'),
            default=sys.stdout
        )
        parser.add_argument(
            "-t",
            "--text",
            action="store_true",
            help="Run AmiOCR on a given Image"
        )
        args = parser.parse_args()
        self.execute(args)

def main():
    """Runs the CLI"""
    pyamiimage = Pyamiimage()
    pyamiimage.handlecli()