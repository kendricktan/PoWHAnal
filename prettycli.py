import colored

from datetime import datetime
from colored import stylize


def std_print(s, c):
    '''
    Standardized printing
    Args:
    s: String to be printed
    c: Color of string, type: string    
    '''
    ds = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    print(stylize('[{}] {}'.format(ds, s), colored.fg(c)))


def print_error(t, log=False):
    '''
    Prints an Error
    e: Error text
    log: Boolean if it should be logged or nah
    '''
    if log:
        pass

    std_print(':( - {}'.format(t), 'red_1')


def print_success(t, log=False):
    if log:
        pass

    std_print(':)  - {}'.format(t), 'green_1')


def print_bid(t, log=False):
    if log:
        pass

    std_print('Bid ! - {}'.format(t), 'sea_green_1a')


def print_ask(t, log=False):
    if log:
        pass

    std_print('Ask ! - {}'.format(t), 'indian_red_1a')


def print_info(t, log=False):
    if log:
        pass

    std_print('Info - {}'.format(t), 'blue_1')
