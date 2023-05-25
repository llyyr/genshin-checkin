import asyncio
import genshin
import os
import time
import sys
import requests
from bs4 import BeautifulSoup

def extract_active_codes():
    url = 'https://genshin-impact.fandom.com/wiki/Promotional_Code'
    res = requests.get(url).text
    soup = BeautifulSoup(res, 'html.parser').select('table')[0].select('tbody')[0].select('tr')[1:]
    codes = set()
    for ele in soup:
        code = ele.select('td')[0].select('a')[0].text
        duration = ele.select('td')[-1].text
        if 'Expired' in duration:
            break
        codes.add(code)
    return codes

def read_file(file):
    if not os.path.exists(file): # Assume all valid codes are already claimed.
        write_file(extract_active_codes(), file)
    with open(file, 'r') as f:
        return f.read().splitlines()

def write_file(codes, file):
    with open(file, 'w') as f:
        f.write('\n'.join(codes))

async def claim_daily(client):
    try:
        result = await client.claim_daily_reward()
    except genshin.AlreadyClaimed:
        print('You have already checked in.')
        return 0
    except genshin.InvalidCookies:
        print('Failed to check in, cookies are not valid.')
        return 1
    except Exception as e:
        print(f'Failed to check in: {e}')
        return 2
    else:
        print(f'Successfully checked in. Got {result.amount} {result.name}(s).')

async def redeem_codes(client):
    codes = extract_active_codes()
    file = 'genshin_codes.txt'
    used_codes = set(read_file(file))
    for code in codes - used_codes:
        print(f'Redeeming code: {code}')
        try:
            await client.redeem_code(code)
        except genshin.RedemptionClaimed:
            print('You have already redeemed this code.')
            return 0
        except genshin.InvalidCookies:
            print('Failed to redeem code, cookies are not valid.')
            return 1
        except Exception as e:
            print(f'Could not redeem code {code}: {e}')
            return 2
        finally:
            used_codes.add(code)
        time.sleep(7)
    write_file(used_codes, file)

async def main():
    cookies = os.environ.get('GENSHIN_COOKIES')
    client = genshin.Client(cookies, game=genshin.Game.GENSHIN)
    client.USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/113.0'
    return await claim_daily(client) or await redeem_codes(client)

if __name__ == '__main__':
    ret = asyncio.run(main())
    sys.exit(ret)
