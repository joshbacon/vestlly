import { Pencil, Trash2, ListPlus, Square, SquareCheck } from 'lucide-react';
import { useOutletContext } from 'react-router-dom';
import { useWatchlists } from '../reducers/WatchlistContext';
import { useEffect, useState } from 'react';
import SectorPieChart from '../components/SectorPieChart';
import Calendar from '../components/Calendar';
import StockPanel from '../components/StockPanel';

function WatchlistPage() {
    const { watchlists, dispatch } = useWatchlists();
    const [ selectedList, setSelectedList ] = useState(null);
    const { marketData } = useOutletContext();

    useEffect(() => {
        if (watchlists.length > 0) {
            setSelectedList(watchlists[0]);
        }
    }, []);

    const dateRanges = ['1D','5D','1M','6M','1Y','5Y'];

    const [ selectedDateRange, setDateRange ] = useState(dateRanges[0]);
    const [ showingEdit, setShowingEdit ] = useState(false);
    const [ editedName, setEditedName ] = useState("New List");
    const [ stocks, setStocks ] = useState([]);
    const [ expanded, setExpanded ] = useState([]);
    const [ dates, setDates ] = useState([]);

    const getStockData = (ticker) => {
        return marketData.findLast((s) => s.symbol === ticker);
    }

    useEffect(() => {
        if (selectedList !== null) {
            setEditedName(selectedList.name);
            setStocks([...new Set(selectedList.tickers.map(item => getStockData(item)))]);
        }
    }, [selectedList]);

    useEffect(() => {
        let tempDates = [];
        stocks.forEach((stock) => {
            stock.history.forEach((day) => {
                try {
                    tempDates.push({
                        ticker: stock.symbol,
                        name: 'Dividend Ex',
                        date: new Date(day.exDividendDate*1000)
                    })
                } catch {}
                try {
                    tempDates.push({
                        ticker: stock.symbol,
                        name: 'Dividend Payout',
                        date: new Date(day.dividendDate*1000)
                    })
                } catch {}
                try {
                    tempDates.push({
                        ticker: stock.symbol,
                        name: 'Earnings',
                        date: new Date(day.earningsTimestamp*1000)
                    })
                } catch {}
            });
        });
        const uniqueArray = tempDates.filter((o, index, arr) =>
            arr.findIndex(item => JSON.stringify(item) === JSON.stringify(o)) === index
        );
        uniqueArray.sort((a, b) => a.date - b.date);
        setDates(uniqueArray);
    }, [stocks]);

    const updateTicker = (ticker) => {
        let temp = {...selectedList};
        if (temp.tickers.includes(ticker)) {
            temp.tickers.splice(temp.tickers.indexOf(ticker), 1);
            dispatch({ type: 'REMOVE_TICKER', listId: selectedList.id, ticker: ticker });
        } else {
            temp = {...temp, tickers: [...temp.tickers, ticker] };
            dispatch({ type: 'ADD_TICKER', listId: selectedList.id, ticker: ticker });
        }
        setselectedList(temp);
    }

    const updateExpanded = ({ symbol }) => {
        if (expanded.includes(symbol)) {
            const temp = [...expanded];
            temp.splice(expanded.indexOf(symbol), 1)
            setExpanded(temp);
        } else  {
            setExpanded([...expanded, symbol]);
        }
    }

    return <div className="w-full h-full flex">
        <div className="flex flex-col gap-3 flex-1 p-3 overflow-y-auto">
            {watchlists.map((list) => (
                <div
                    key={list.id}
                    className="bg-teal-900/45 rounded-2xl p-3 cursor-pointer"
                    onClick={() => setSelectedList(list)}
                >
                    <h1 className="font-bold">{list.name}</h1>
                    <ul className="text-right">
                        {list.tickers.map((ticker) => {
                            return <li key={ticker}>{ticker}</li>
                        })}
                    </ul>
                </div>
            ))}
            <div
                className="flex justify-center place-items-center bg-teal-950/45 hover:bg-teal-900/45 cursor-pointer rounded-2xl p-3"
                onClick={() => dispatch({ type: 'CREATE_LIST', name: 'New List' })}
            >
                <ListPlus />
            </div>
        </div>
        
        {
            selectedList === null ? 
            <div className='flex justify-center place-items-center gap-3 flex-3 p-5 bg-mist-900'>
                Select or create a watchlist to see stats here
            </div>
            :
            <div className="flex flex-col gap-3 flex-3 p-5 bg-mist-900 overflow-y-auto">
                <div className="flex justify-between place-items-center">
                    <div className='flex gap-1'>
                        <h1 className="text-2xl font-bold">{selectedList.name}</h1>
                        {/* <div className='flex px-2 rounded-2xl'>
                            { dateRanges.map((range) => {
                                return <p key={range}
                                    onClick={() => setDateRange(range)}
                                        className={range === selectedDateRange ?
                                            'cursor-pointer px-2 py-1 rounded-2xl bg-teal-900/80' :
                                            'cursor-pointer px-2 py-1 rounded-2xl hover:bg-teal-900'
                                        }
                                    >
                                        {range}
                                    </p>
                            })}
                        </div> */}
                    </div>
                    <button
                        className='cursor-pointer'
                        onClick={() => setShowingEdit(!showingEdit)}
                    >
                        <Pencil color="#00786f"/>
                    </button>
                </div>
                <div className='flex'>
                    <div className={"transition-[width] duration-450 ease-in-out overflow-hidden bg-mist-950 rounded-2xl h-52 flex justify-center place-items-center " + (!showingEdit ? 'w-full' : 'w-0')}>
                        <p>graph of performance here</p>
                    </div>
                    <div className={'transition-[width] duration-450 ease-in-out overflow-hidden h-52 bg-mist-950/30 rounded ' + (showingEdit ? 'w-full' : 'w-0')}>
                        <div className='flex justify-between place-items-center p-3'>
                            <div className='flex gap-3 place-items-center'>
                                <p className='font-semibold'>Name: </p>
                                <input
                                    type="text"
                                    value={editedName}
                                    onChange={({ target }) => setEditedName(target.value)}
                                    onBlur={() => {
                                        dispatch({ type: 'RENAME_LIST', listId: selectedList.id, name: editedName });
                                        setSelectedList({...selectedList, name: editedName});
                                    }}
                                    className='outline-0 bg-mist-800 rounded p-1'
                                />
                            </div>
                            <button
                                className='cursor-pointer'
                                onClick={() => {
                                    setSelectedList(null);
                                    setShowingEdit(false);
                                    dispatch({ type: 'DELETE_LIST', listId: selectedList.id });
                                }}
                            >
                                <Trash2 color="#e92121" />
                            </button>
                        </div>
                        <div className='flex flex-wrap gap-3 p-2'>
                            {marketData.length > 0 ? marketData.map((data) => {
                                return <div
                                    key={data.symbol}
                                    className='flex gap-1 cursor-pointer'
                                    onClick={() => updateTicker(data.symbol)}
                                >
                                    {selectedList.tickers.includes(data.symbol) ? <SquareCheck color="#00786f"/> : <Square />}
                                    <p className='select-none'>{data.symbol}</p>
                                </div>
                            }) : <></>}
                        </div>
                    </div>
                </div>
                <ul className="flex flex-col gap-1 pb-4">
                    {stocks.map((stock) => {
                        const hist = stock.history;
                        const currPrice = hist[hist.length-1].currentPrice;
                        const diff = currPrice - hist[hist.length-1].open;
                        return <div key={stock.symbol}>
                            <div>
                                <li
                                    className='flex justify-between p-2 cursor-pointer bg-mist-950/50 rounded-t-2xl'
                                    onClick={() => updateExpanded(stock)}
                                >
                                    <h3 className='flex-4'>{stock.symbol}</h3>
                                    <div className='flex flex-1 justify-between'>
                                        <p className={diff >= 0 ? 'text-green-400' : 'text-red-400'}>${diff.toFixed(2)}</p>
                                        <p>${currPrice}</p>
                                    </div>
                                </li>
                                <div className={'grid transition-all duration-500 ' + (expanded.includes(stock.symbol) ? 'grid-rows-[1fr]' : 'grid-rows-[0fr]')}>
                                    <StockPanel stock={stock} />
                                </div>
                            </div>
                            <hr className='h-px bg-teal-700 border-0'/>
                        </div>
                    })}
                </ul>
                <div className="flex flex-col gap-3">
                    <div className=''>
                        <h1 className='font-semibold'>Sector Breakdown</h1>
                        <SectorPieChart marketData={stocks}/>
                    </div>
                    <div className="bg-mist-950 rounded-2xl p-3">
                        <Calendar events={dates} />
                    </div>
                </div>
            </div>
        }
    </div>
}

export default WatchlistPage;