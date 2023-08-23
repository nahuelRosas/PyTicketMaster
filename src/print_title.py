from colorama import Fore
from src.print_multiline import print_multiline

def print_title() -> None:
    """
    Prints the program title in ASCII art format.
    """
    title = r"""
 _____                _               _       ______                 _              _    
|_   _|              | |             ( )      | ___ \               (_)            | |  
  | |    __ _  _   _ | |  ___   _ __ |/  ___  | |_/ / _ __   ___     _   ___   ___ | |_ 
  | |   / _` || | | || | / _ \ | '__|   / __| |  __/ | '__| / _ \   | | / _ \ / __|| __|
  | |  | (_| || |_| || || (_) || |      \__ \ | |    | |   | (_) |  | ||  __/| (__ | |_ 
  \_/   \__,_| \__, ||_| \___/ |_|      |___/ \_|    |_|    \___/   | | \___| \___| \__|
                __/ |                                              _/ |                 
               |___/                                              |__/                  
               
            By: Nahuel Rosas - Github: https://github.com/nahuelRosas          
    """
    print_multiline(title, Fore.LIGHTCYAN_EX, "center")

if __name__ == "__main__":
    print_title()