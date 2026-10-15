import data
import library
import trader
import model
from tqdm import tqdm

## Load in the data for each stock once instead of once per indicator
def refresh_data() -> list[dict]:
    # return data.read_local()
    market_data = []
    market_data.append(data.fetch_all_stocks(library.sectors[0], True))
    # for sector in tqdm(
    #     library.sectors,
    #     desc=f"Loading Sectors",
    #     colour="blue",
    #     ncols=96,
    #     unit="sectors"
    # ):
    #     market_data.append(data.fetch_all_stocks(sector, True))
    return market_data

## Test all the stocks against the trained model for their respective sectors
def parse_data(data: list[dict]) -> list[dict]:
    results = []
    results.extend(model.evaluate_sector(data[0]))
    # for sector in tqdm(
    #     data,
    #     desc=f"Evaluating Stocks",
    #     colour="yellow",
    #     ncols=88,
    #     unit="sectors"
    # ):
    #     results.extend(model.evaluate_sector(sector))
    return results

## Make any resulting trades
def make_trades(trades: list[dict]) -> list[dict]:
    results = []
    for trade in trades:
        results.extend(trader.execute_trade(trade))
    return results


## All together now
def runner():
    window = refresh_data()
    if len(window) < 1:
        return []
    trades = parse_data(window)
    for t in trades:
        print(t)
    # if len(trades) < 1:
    #     return []
    # return make_trades(trades)

runner()