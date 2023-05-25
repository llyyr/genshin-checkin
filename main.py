import asyncio
import genshin
import os
import sys


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

async def main():
    cookies = os.environ.get('GENSHIN_COOKIES')
    client = genshin.Client(cookies, game=genshin.Game.GENSHIN)
    client.USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/113.0'
    return await claim_daily(client)

if __name__ == '__main__':
    ret = asyncio.run(main())
    sys.exit(ret)
