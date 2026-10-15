import { useEffect, useState } from 'react';
import { ChevronRight, ChevronLeft } from 'lucide-react';
import { useWatchlists } from '../reducers/WatchlistContext';
import { useOutletContext } from 'react-router-dom';
import Calendar from '../components/Calendar';

function CalendarPage() {
    const { watchlists, dispatch } = useWatchlists();
    const [ selectedLists, setSelectedLists ] = useState([...watchlists]);
    const { marketData } = useOutletContext();
    const [ dates, setDates ] = useState([]);

    const getStockData = (ticker) => {
        return marketData.findLast((s) => s.symbol === ticker);
    }

    useEffect(() => {
        if (selectedLists.length === 0) {
            setDates([]);
            return;
        }
        const uniqueTickers = [];
        selectedLists.forEach((l) => {
            if (l.tickers.length > 0) {
                l.tickers.forEach((t) => {
                    if (!uniqueTickers.includes(t)) {
                        uniqueTickers.push(t);
                    }
                });
            }
        });
        const tempDates = [];
        uniqueTickers.forEach((stock) => {
            const data = getStockData(stock);
            data.history.forEach((day) => {
                try {
                    tempDates.push({
                        ticker: stock,
                        name: 'Dividend Ex',
                        date: new Date(day.exDividendDate*1000)
                    })
                } catch {}
                try {
                    tempDates.push({
                        ticker: stock,
                        name: 'Dividend Payout',
                        date: new Date(day.dividendDate*1000)
                    })
                } catch {}
                try {
                    tempDates.push({
                        ticker: stock,
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
    }, [selectedLists]);

    const updateSelected = (wl) => {
        if (selectedLists.includes(wl)) {
            const temp = [...selectedLists];
            temp.splice(selectedLists.indexOf(wl), 1)
            setSelectedLists(temp);
        } else  {
            setSelectedLists([...selectedLists, wl]);
        }
    }

    return <div>
        <div className="flex gap-3 p-3">
            {watchlists.map((wl) => {
                return <p
                    key={wl.id}
                    className={"px-2 cursor-pointer border-2 border-teal-700 rounded-md" + (selectedLists.includes(wl) ? ' bg-teal-700' : '')}
                    onClick={() => updateSelected(wl)}
                >
                    {wl.name}
                </p>
            })}
        </div>
        <hr/>
        <div className='p-3'>
            <Calendar events={dates} />
        </div>
    </div>
}

export default CalendarPage;