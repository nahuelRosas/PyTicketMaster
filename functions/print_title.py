from functions.print_multiline import print_multiline
from colorama import Fore, Style


def print_title():
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
