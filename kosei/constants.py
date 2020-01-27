import enum

import colorama


class Sources(enum.Enum):
    OVERRIDED = {"color": colorama.Fore.RED}
    BINDED = {"color": colorama.Fore.RESET}
    ENVVAR = {"color": colorama.Fore.BLUE}
    FILE = {"color": colorama.Fore.WHITE}
    DOTENV = {"color": colorama.Fore.GREEN}
