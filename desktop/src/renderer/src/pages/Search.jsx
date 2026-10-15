import { useEffect, useState } from 'react';
import { useWatchlists } from '../reducers/WatchlistContext';
import { ChartNetwork, ListPlus } from 'lucide-react';
import PriceChart from '../components/PriceChart';

function SearchPage() {

    const [ searchTerm, setSearchTerm ] = useState("");
    const [ searchResults, setSearchResults ] = useState([]);
    const [ selectedStock, setSelectedStock ] = useState(null);
    const { watchlists, dispatch } = useWatchlists();
    const [ showingWatchlist, setShowingWatchlist ] = useState(false);

    const searchStock = async (input) => {
        const res = await fetch(`http://localhost:8000/api/search/${input}`);
        if (!res.ok) throw new Error("Failed to fetch stock data");
        return res.json();
    }

    const fetchStock = async (input) => {
        const res = await fetch(`http://localhost:8000/api/stock/${input}`);
        if (!res.ok) throw new Error("Failed to fetch stock data");
        return res.json();
    }

	useEffect(() => {
        if (searchTerm.trim().length < 2) {
            setSearchResults([]);
            return;
        }
		const debounceTimer = setTimeout(async () => {
            const data = await searchStock(searchTerm);
            setSearchResults(data.results || []);
		}, 1000);

		return () => clearTimeout(debounceTimer);
	}, [searchTerm]);

    const handleStockSelect = async (ticker) => {
        const data = await fetchStock(ticker);
        console.log(data);
        setSelectedStock(data || null);
    }

    const updateList = (list) => {
        if (selectedStock == null) return;
        let temp = {...list};
        const ticker = selectedStock.symbol;
        if (temp.tickers.includes(ticker)) {
            temp.tickers.splice(temp.tickers.indexOf(ticker), 1);
            dispatch({ type: 'REMOVE_TICKER', listId: list.id, ticker: ticker });
        } else {
            temp = {...temp, tickers: [...temp.tickers, ticker] };
            dispatch({ type: 'ADD_TICKER', listId: list.id, ticker: ticker });
        }
    }

    return <div className="w-full h-full flex flex-col justify-center place-items-center">
        <div className='py-5 relative w-min flex flex-col gap-2'>
            <input
                type="text"
                value={searchTerm}
                placeholder="ex. CM.TO"
                autoFocus="true"
                className="bg-mist-800 rounded-lg py-1 px-2 min-w-60 outline-0"
                onChange={({ target }) => setSearchTerm(target.value)}
            />
            { searchResults.length > 0 ?
                <div className='absolute top-[85%] z-10 bg-mist-800 rounded-xl p-3 w-full flex flex-col gap-1'>
                    {searchResults.map((result, i) => {
                        return <div
                            key={`${result.symbol}-${i}`}
                            className='cursor-pointer text-center hover:bg-mist-700/50 rounded-md'
                            onClick={() => {
                                handleStockSelect(result.symbol);
                                setSearchResults([]);
                            }}
                        >
                            {result.symbol}
                        </div>
                    })}
                </div> : <></>
            }
        </div>
        { selectedStock != null ?
            <div className='w-full overflow-y-auto p-3 flex flex-col gap-3 flex-1 bg-mist-900/80'>
                <div className='flex justify-between place-items-center pl-20 pr-5'>
                    <div>
                        <div className='flex gap-2 place-items-center'>
                            <h1 className='font-bold text-lg'>{selectedStock.symbol}</h1>
                            <h2 className='font-bold text-lg'>${selectedStock.price}</h2>
                            <h2
                                className={'font-bold text-lg ' + (selectedStock.price > selectedStock.history[selectedStock.history.length-2].Close ? 'text-green-400' : 'text-red-400')}
                            >({(((1-(selectedStock.history[selectedStock.history.length-2].Close/selectedStock.price))*100).toFixed(2))}%)</h2>
                        </div>
                        <div className='flex gap-2 place-items-center'>
                            <h2 className='text-sm font-light'>{selectedStock.name}</h2>
                            <h2 className='text-sm font-light'>-</h2>
                            <h2 className='text-sm font-light'>{selectedStock.info.exchange}</h2>
                        </div>
                    </div>
                    <div className='relative'>
                        <button
                            onClick={() => setShowingWatchlist(!showingWatchlist)}
                            className='cursor-pointer'
                            title='Add to Watchlist'
                        >
                            <ListPlus size={26} />
                        </button>
                        { showingWatchlist ? 
                            <div className='absolute right-[120%] z-10 top-0 rounded-2xl bg-mist-900 overflow-y-auto'>
                                { watchlists.map((list) => (
                                    <div
                                        key={list.id}
                                        className={"hover:bg-teal-700 p-3 cursor-pointer text-center " + (list.tickers.includes(selectedStock.symbol) ? 'bg-teal-900' : '')}
                                        onClick={() => updateList(list)}
                                    >
                                        <h1 className="font-bold">{list.name}</h1>
                                    </div>
                                ))}
                            </div> :
                            <></>
                        }
                    </div>
                </div>
                <PriceChart data={selectedStock.history} />
                <div className='py-3 px-5 grid grid-cols-4 gap-x-11 gap-y-2'>
                    <div className='flex justify-between place-items-center border-b border-dashed border-teal-700'>
                        <p className='font-extralight text-sm text-left'>Forward P/E:</p>
                        <p className='font-medium text-sm text-right'>{selectedStock.info.forwardPE != null ? selectedStock.info.forwardPE.toFixed(2) : 'none'}</p>
                    </div>
                    <div className='flex justify-between place-items-center border-b border-dashed border-teal-700 pb-1'>
                        <p className='font-extralight text-sm text-left'>PEG:</p>
                        <p className='font-medium text-sm text-right'>{selectedStock.info.pegRatio != null ? selectedStock.info.pegRatio.toFixed(2) : 'none'}</p>
                    </div>
                    <div className='flex justify-between place-items-center border-b border-dashed border-teal-700 pb-1'>
                        <p className='font-extralight text-sm text-left'>50 Day Avg:</p>
                        <p className='font-medium text-sm text-right'>{selectedStock.info.fiftyDayAverage != null ? '$'+selectedStock.info.fiftyDayAverage.toFixed(2) : 'none'}</p>
                    </div>
                    <div className='flex justify-between place-items-center border-b border-dashed border-teal-700 pb-1'>
                        <p className='font-extralight text-sm text-left'>Dividend Rate:</p>
                        <p className='font-medium text-sm text-right'>{selectedStock.info.dividendRate != null ? '$'+selectedStock.info.dividendRate.toFixed(2) : 'none'}</p>
                    </div>
                    <div className='flex justify-between place-items-center border-b border-dashed border-teal-700 pb-1'>
                        <p className='font-extralight text-sm text-left'>Trainling P/E:</p>
                        <p className='font-medium text-sm text-right'>{selectedStock.info.trailingPE != null ? selectedStock.info.trailingPE.toFixed(2) : 'none'}</p>
                    </div>
                    <div className='flex justify-between place-items-center border-b border-dashed border-teal-700 pb-1'>
                        <p className='font-extralight text-sm text-left'>P/S:</p>
                        <p className='font-medium text-sm text-right'>{selectedStock.info.priceToSalesTrailing12Months != null ? selectedStock.info.priceToSalesTrailing12Months.toFixed(2) : ''}</p>
                    </div>
                    <div className='flex justify-between place-items-center border-b border-dashed border-teal-700 pb-1'>
                        <p className='font-extralight text-sm text-left'>200 Day Avg:</p>
                        <p className='font-medium text-sm text-right'>{selectedStock.info.twoHundredDayAverage != null ? '$'+selectedStock.info.twoHundredDayAverage.toFixed(2) : 'none'}</p>
                    </div>
                    <div className='flex justify-between place-items-center border-b border-dashed border-teal-700 pb-1'>
                        <p className='font-extralight text-sm text-left'>Dividend Yield:</p>
                        <p className='font-medium text-sm text-right'>{selectedStock.info.dividendYield != null ? selectedStock.info.dividendYield.toFixed(2)+'%' : 'none'}</p>
                    </div>
                    <div className='flex justify-between place-items-center border-b border-dashed border-teal-700 pb-1'>
                        <p className='font-extralight text-sm text-left'>Short Ratio:</p>
                        <p className='font-medium text-sm text-right'>{selectedStock.info.shortRatio != null ? selectedStock.info.shortRatio.toFixed(2) : 'none'}</p>
                    </div>
                    <div className='flex justify-between place-items-center border-b border-dashed border-teal-700 pb-1'>
                        <p className='font-extralight text-sm text-left'>P/B:</p>
                        <p className='font-medium text-sm text-right'>{selectedStock.info.priceToBook != null ? selectedStock.info.priceToBook.toFixed(2) : 'none'}</p>
                    </div>
                    <div className='flex justify-between place-items-center border-b border-dashed border-teal-700 pb-1'>
                        <p className='font-extralight text-sm text-left'>52 Week Range:</p>
                        <p className='font-medium text-sm text-right'>{selectedStock.info.fiftyTwoWeekLow != null ? '$'+selectedStock.info.fiftyTwoWeekLow.toFixed(2) : ''} - {selectedStock.info.fiftyTwoWeekHigh != null ? '$'+selectedStock.info.fiftyTwoWeekHigh.toFixed(2) : ''}</p>
                    </div>
                    <div className='flex justify-between place-items-center border-b border-dashed border-teal-700 pb-1'>
                        <p className='font-extralight text-sm text-left'>Dividend Payout Ratio:</p>
                        <p className='font-medium text-sm text-right'>{selectedStock.info.payoutRatio != null ? selectedStock.info.payoutRatio.toFixed(2)+'%' : 'none'}</p>
                    </div>
                    <div className='flex justify-between place-items-center border-b border-dashed border-teal-700 pb-1'>
                        <p className='font-extralight text-sm text-left'>Forward EPS:</p>
                        <p className='font-medium text-sm text-right'>{selectedStock.info.epsForward != null ? selectedStock.info.epsForward.toFixed(2) : 'none'}</p>
                    </div>
                    <div className='flex justify-between place-items-center border-b border-dashed border-teal-700 pb-1'>
                        <p className='font-extralight text-sm text-left'>EPS:</p>
                        <p className='font-medium text-sm text-right'>{selectedStock.info.epsCurrentYear != null ? selectedStock.info.epsCurrentYear.toFixed(2) : 'none'}</p>
                    </div>
                    <div className='flex justify-between place-items-center border-b border-dashed border-teal-700 pb-1'>
                        <p className='font-extralight text-sm text-left'>Analyst:</p>
                        <p className='font-medium text-sm text-right'>{selectedStock.info.averageAnalystRating != null ? selectedStock.info.averageAnalystRating : 'none'}</p>
                    </div>
                    <div className='flex justify-between place-items-center border-b border-dashed border-teal-700 pb-1'>
                        <p className='font-extralight text-sm text-left'>Book Value:</p>
                        <p className='font-medium text-sm text-right'>{selectedStock.info.bookValue != null ? '$'+selectedStock.info.bookValue.toFixed(2) : 'none'}</p>
                    </div>
                    <div className='flex justify-between place-items-center border-b border-dashed border-teal-700 pb-1'>
                        <p className='font-extralight text-sm text-left'>RoE:</p>
                        <p className='font-medium text-sm text-right'>{selectedStock.info.returnOnEquity != null ? (selectedStock.info.returnOnEquity*100).toFixed(2)+'%' : 'none'}</p>
                    </div>
                    <div className='flex justify-between place-items-center border-b border-dashed border-teal-700 pb-1'>
                        <p className='font-extralight text-sm text-left'>D/E:</p>
                        <p className='font-medium text-sm text-right'>{selectedStock.info.debtToEquity != null ? selectedStock.info.debtToEquity.toFixed(2) : 'none'}</p>
                    </div>
                    <div className='flex justify-between place-items-center border-b border-dashed border-teal-700 pb-1'>
                        <p className='font-extralight text-sm text-left'>Target Range:</p>
                        <p className='font-medium text-sm text-right'>{selectedStock.info.targetLowPrice != null ? '$'+selectedStock.info.targetLowPrice.toFixed(2) : ''} - {selectedStock.info.targetHighPrice != null ? '$'+selectedStock.info.targetHighPrice.toFixed(2) : ''}</p>
                    </div>
                    <div className='flex justify-between place-items-center border-b border-dashed border-teal-700 pb-1'>
                        <p className='font-extralight text-sm text-left'>Beta:</p>
                        <p className='font-medium text-sm text-right'>{selectedStock.info.beta != null ? selectedStock.info.beta.toFixed(2) : 'none'}</p>
                    </div>
                    <div className='flex justify-between place-items-center border-b border-dashed border-teal-700 pb-1'>
                        <p className='font-extralight text-sm text-left'>RoA:</p>
                        <p className='font-medium text-sm text-right'>{selectedStock.info.returnOnAssets != null ? (selectedStock.info.returnOnAssets*100).toFixed(2)+'%' : 'none'}</p>
                    </div>
                </div>
            </div> : <></>
        }
    </div>
}

export default SearchPage;