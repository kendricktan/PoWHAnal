import math
import re
import requests
import time

from functools import reduce
from prettycli import print_info, print_success, print_error, print_bid

def get_current_block():
    r = requests.get('https://www.etherchain.org/api/basic_stats').json()
    return r['blocks'][0]['number']


def get_etherscan_tx(hash):
    url = 'https://etherscan.io/tx/' + hash

    content = requests.get(url).text
    content = content.replace('<b>.</b>', '.')
    regex = r'TRANSFER &nbsp;([\d.]+) Ether'
    p = re.findall(regex, content)
    try:
        return float(p[0])
    except:
        return 0.0


def get_etherscan_anal(idx, block_height, blocks_prior=600, init_dict={'buy': {}, 'sell': {}, 'buy_highest': 0, 'sell_highest': 0, 'lowest_block': 1e+20}):
    '''
    Analytics for etherdelta. 
    Graph the last 300 seconds (~30 blocks), volume of buy/sell

    Params:
        idx: etherscan url index
        block_height: current block height
        blocks_prior: keep scanning until you hit X blocks prior
                      1 block ~10 sec
        init_dict: Think of it as a state monad lmao but its not :(
    '''
    url = 'https://etherscan.io/txs?a=0xa7ca36f7273d4d38fc2aec5a454c497f86728a7a&p=' + str(idx)

    if idx > 1:
        print_info('Getting page: {}, lowest block height: {}, target block height: {}'.format(idx, block_height - blocks_prior, init_dict['lowest_block']))
    else:
        print_info('Initializing etherscan...')

    content = requests.get(url).text
    content = content.replace('<b>.</b>', '.')
    regex_q = r"<span class='address-tag'><a href='\/tx\/(\w+)\'>\w+<\/a><\/span><\/td><td class=[\w\s\=\'\"\-\:]+><a href='\/block\/(\d+)\'>\d+<\/a><\/td><td><[\w\s\=\'\"\-\:]+>[\w\s]+<\/span><\/td><td><span class='address-tag'><a href='\/address\/(\w+)\'>\w+<\/a><\/span><\/td><td><[\w\s\=\'\"\-\:]+>[\w\s\=\'\"\-\:\&\;]+<\/span><\/td><td><[\w\s\=\'\"\-\:\;]+><[\w\s\=\'\"\-\:\;]+><\/i>\s*<span class='address-tag'>(\w+)<\/span><\/span><\/td><td>([\d.]+)\s+Ether"
    p = re.findall(regex_q, content)    

    # from, block height, hash, to, value
    def f(x, y):
        '''
        x: buy_sell_dict
        y: item from p
           having property (from, block height, hash, to, value)
        '''
        _hash, _bh, _from, _to, _val = y

        _bh = int(_bh)
        _val = float(_val)

        # Index for buy/sell dict        
        k = max(math.floor((block_height - _bh) / 30.0), 0)

        # BUY        
        if _val > 0:
            x['buy'][str(k)] = getattr(x['buy'], str(k), 0) + _val
            x['buy_highest'] = max(x['buy_highest'], k)            

        # SELL
        else:
            _sell_val = get_etherscan_tx(_hash)
            x['sell'][str(k)] = getattr(x['sell'], str(k), 0) + _sell_val
            x['sell_highest'] = max(k, x['sell_highest'])                

        x['lowest_block'] = min(x['lowest_block'], _bh)

        return x
    
    processed_dict = reduce(f, p, init_dict)

    # Hit our lowest threshold
    if (processed_dict['lowest_block'] < (block_height - blocks_prior)):
        return processed_dict

    return get_etherscan_anal(idx + 1, block_height, blocks_prior, processed_dict)

if __name__ == '__main__':
    while True:
        blocks_prior = 300
        block_height = get_current_block()
        anal = get_etherscan_anal(1, block_height, blocks_prior)

        print_info('-------------')

        # Get maximum
        imax = max(anal['buy_highest'], anal['sell_highest'])

        # Just see if there's more buying than selling
        for i in range(imax):
            _in = anal['buy'][str(i)]
            _out = anal['sell'][str(i)]

            if _in > _out:
                p = print_success
            else:
                p = print_error

            p('Total buy: :{:.4f}\t| Total sell: {:.4f}\t| Net: {:.4f}\t| {} mins ago'.format(
                _in, _out, _in - _out, i * (blocks_prior / 10)
            ))

        print_info('-------------')
        print_info('Sleeping for 60 seconds...')
                
        time.sleep(60)