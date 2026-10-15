import os
from pprint import pprint
from dotenv import load_dotenv
from snaptrade_client import SnapTrade

## Load in environment variables
load_dotenv()
client_id = os.getenv("CLIENT_ID")
secret = os.getenv("SECRET")
user_id = os.getenv("USER_ID")
user_secret = os.getenv("USER_SECRET")
account_id = os.getenv("ACCOUNT_ID")

# snaptrade = SnapTrade(
#     client_id=client_id,
#     consumer_key=secret
# )



# data = snaptrade.account_information.get_user_holdings(
#     account_id=account_id,
#     user_id=user_id,
#     user_secret=user_secret
# )




# print(data, file=open('output.txt', 'w'))


