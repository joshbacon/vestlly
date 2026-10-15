import { useEffect, useState } from 'react';
import { useOutletContext } from 'react-router-dom';
import { useWatchlists } from '../reducers/WatchlistContext';
import StockPanel from '../components/StockPanel';
import IndicatorChart from '../components/IndicatorChart';

function AnalysisPage() {

    const { watchlists, dispatch } = useWatchlists();
    const { marketData } = useOutletContext();
    const [ selectedStock, setSelectedStock ] = useState(marketData[0]);
    const [ showingMenu, setShowingMenu ] = useState(false);
    const [ menu, setMenu ] = useState({});

    useEffect(() => {
        let temp = {};
        marketData.forEach((stock) => {
            const sector = stock.meta.sector;
            if (sector in temp && !(stock.symbol in temp[sector])) {
                temp[sector].push(stock);
            } else {
                temp[sector] = [stock];
            }
        });
        setMenu(temp);
    }, []);

    const updateSelectedStock = (stock) => {
        setSelectedStock(stock);
        setShowingMenu(false);
    }

    return <div>
        <div className='relative w-full flex flex-col gap-2'>
            <div
                className='cursor-pointer w-30 bg-mist-900 rounded-lg m-3 p-2'
                onClick={() => {
                    setShowingMenu(!showingMenu)
                }}
            >
                <h1>{selectedStock.symbol}</h1>
            </div>
            <div className={'flex flex-wrap gap-3 pl-3 bg-mist-800 overflow-y-auto transition-[height] ease-in-out duration-500 ' + (showingMenu ? 'h-50' : 'h-0')}>
                {
                    [...Object.keys(menu)].map((value) => {
                        // console.log(value);
                        const data = menu[value];
                        // console.log(data);
                        return <div className='w-fit pb-3'>
                            <h1 className='border-b border-dotted p-2 mb-1 border-b-teal-800'>{value}</h1>
                            <ul
                                className='grid grid-cols-3'
                            >
                                {data.map((stock) => {
                                    return <li
                                        className='cursor-pointer hover:bg-mist-700 px-2 rounded-sm'
                                        onClick={() => updateSelectedStock(stock)}
                                    >
                                        <h1>{stock.symbol}</h1>
                                    </li>
                                })}
                            </ul>
                        </div>
                    })
                }
            </div>
        </div>
        <div className='flex flex-wrap'>
            <div className='w-full flex justify-center text-center'>
                <ul>
                    <li>include the stock evaluation results up here</li>
                    <li>have one trained for each sector or something</li>
                </ul>
            </div>
            <StockPanel stock={selectedStock}/>
            <div className='w-full min-w-100 p-3'>
                <h1 className='text-right font-semibold'>Price History</h1>
                <IndicatorChart data={selectedStock.history} tag={'Current Value'} column={'currentPrice'} tagT={'52 Week High/Low'} columnT={'fiftyTwoWeekLow'} columnE={'fiftyTwoWeekHigh'} tagF={'Target High/Low'} columnF={'targetLowPrice'} columnS={'targetHighPrice'} />
            </div>
            <div className='w-[50%] min-w-100 aspect-video p-3'>
                <h1 className='text-right font-semibold'>Book Value History</h1>
                <IndicatorChart data={selectedStock.history} tag={'Book Value'} column={'bookValue'} tagT={'Market Value'} columnT={'currentPrice'}/>
            </div>
            <div className='w-[50%] min-w-100 aspect-video p-3'>
                <h1 className='text-right font-semibold'>Moving Averages</h1>
                <IndicatorChart data={selectedStock.history} tag={'50 Day'} column={'fiftyDayAverage'} tagT={'200 Day'} columnT={'twoHundredDayAverage'}/>
            </div>
            <div className='w-[50%] min-w-100 aspect-video p-3'>
                <h1 className='text-right font-semibold'>EPS History</h1>
                <IndicatorChart data={selectedStock.history} tag={'EPS'} column={'epsCurrentYear'} tagT={'Forward EPS'} columnT={'forwardEps'}/>
            </div>
            <div className='w-[50%] min-w-100 aspect-video p-3'>
                <h1 className='text-right font-semibold'>P/E History</h1>
                <IndicatorChart data={selectedStock.history} tag={'Trailing PE'} column={'trailingPE'} tagT={'Forward PE'} columnT={'forwardPE'}/>
            </div>
            <div className='w-[50%] min-w-100 aspect-video p-3'>
                <h1 className='text-right font-semibold'>P/B History</h1>
                <IndicatorChart data={selectedStock.history} tag={'P/B'} column={'priceToBook'}/>
            </div>
            <div className='w-[50%] min-w-100 aspect-video p-3'>
                <h1 className='text-right font-semibold'>D/E History</h1>
                <IndicatorChart data={selectedStock.history} tag={'D/E'} column={'debtToEquity'}/>
            </div>
            <div className='w-[50%] min-w-100 aspect-video p-3'>
                <h1 className='text-right font-semibold'>Dividend Rate History</h1>
                <IndicatorChart data={selectedStock.history} tag={'Dividend Rate'} column={'dividendRate'}/>
            </div>
            <div className='w-[50%] min-w-100 aspect-video p-3'>
                <h1 className='text-right font-semibold'>PEG History</h1>
                <IndicatorChart data={selectedStock.history} tag={'PEG'} column={'pegRatio'}/>
            </div>
        </div>
    </div>
}

export default AnalysisPage;