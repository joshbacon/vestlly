import { ChevronRight, ChevronLeft } from 'lucide-react';
import { useState } from 'react';

const WEEKDAYS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

function getMonthMatrix(year, month) {
  // month is 0-indexed
  const firstOfMonth = new Date(year, month, 1);
  const startDay = firstOfMonth.getDay(); // 0 = Sunday
  const daysInMonth = new Date(year, month + 1, 0).getDate();
  const daysInPrevMonth = new Date(year, month, 0).getDate();
 
  const cells = [];
 
  // leading days from previous month
  for (let i = startDay - 1; i >= 0; i--) {
    cells.push({
      day: daysInPrevMonth - i,
      currentMonth: false,
      date: new Date(year, month - 1, daysInPrevMonth - i),
    });
  }
 
  // days in current month
  for (let d = 1; d <= daysInMonth; d++) {
    cells.push({ day: d, currentMonth: true, date: new Date(year, month, d) });
  }
 
  // trailing days to complete the final week
  while (cells.length % 7 !== 0) {
    const nextDay = cells.length - (startDay + daysInMonth) + 1;
    cells.push({
      day: nextDay,
      currentMonth: false,
      date: new Date(year, month + 1, nextDay),
    });
  }
 
  // group into weeks
  const weeks = [];
  for (let i = 0; i < cells.length; i += 7) {
    weeks.push(cells.slice(i, i + 7));
  }
  return weeks;
}
 
function isSameDay(a, b) {
  return (
    a.getFullYear() === b.getFullYear() &&
    a.getMonth() === b.getMonth() &&
    a.getDate() === b.getDate()
  );
}

function Calendar({ events = [] }) {
    const today = new Date();
    const [cursor, setCursor] = useState(new Date(today.getFullYear(), today.getMonth(), 1));

    const year = cursor.getFullYear();
    const month = cursor.getMonth();
    const weeks = getMonthMatrix(year, month);

    const monthLabel = cursor.toLocaleDateString("en-US", {
        month: "long",
        year: "numeric",
    });

    const eventsByDate = {};
    for (const ev of events) {
        const key = new Date(ev.date).toDateString();
        if (!eventsByDate[key]) eventsByDate[key] = [];
        eventsByDate[key].push(ev);
    }

    function goToPrevMonth() {
        setCursor(new Date(year, month - 1, 1));
    }

    function goToNextMonth() {
        setCursor(new Date(year, month + 1, 1));
    }

    function goToToday() {
        setCursor(new Date(today.getFullYear(), today.getMonth(), 1));
    }

    return <div>
        <div className="flex px-4 justify-between place-items-center">
            <h1 className='font-semibold'>{monthLabel}</h1>
            <div className='flex gap-2 pt-2 pl-2'>
                <p className='px-2 font-semibold rounded bg-fuchsia-700/75'>Earnings</p>
                <p className='px-2 font-semibold rounded bg-orange-700/75'>Dividend Ex</p>
                <p className='px-2 font-semibold rounded bg-emerald-700/75'>Dividend Payout</p>
            </div>
        </div>
        <div className="flex gap-2 place-items-center p-2">
            <button
                className='cursor-pointer'
                onClick={goToPrevMonth}
            >
                <ChevronLeft color="#00786f"/>
            </button>
            <h2
                className='font-semibold cursor-pointer'
                onClick={goToToday}
            >
                Today
            </h2>
            <button
                className='cursor-pointer'
                onClick={goToNextMonth}
            >
                <ChevronRight color="#00786f"/>
            </button>
        </div>
        <div className="grid grid-cols-7 px-2 pt-3">
            {WEEKDAYS.map((wd) => (
            <div
                key={wd}
                className="cursor-default text-center text-sm font-medium text-slate-400 uppercase tracking-wide py-1"
            >
                {wd}
            </div>
            ))}
        </div>
        <div className="grid grid-cols-7 gap-1 px-2 pb-3">
            {weeks.flat().map((cell, idx) => {
                const isToday = isSameDay(cell.date, today);
                const dayEvents = eventsByDate[cell.date.toDateString()] || [];
                return <div
                    key={idx}
                    className={
                        'cursor-default outline-1 outline-teal-900 w-full aspect-square pt-3 px-4 overflow-y-auto ' +
                        (cell.currentMonth ? '' : 'text-white/35 ') +
                        (isToday ? 'bg-teal-700/15' : '')
                    }
                >
                    <h1>{cell.day}</h1>
                    {dayEvents.length > 0 && (
                        <div className="mt-1 flex flex-col gap-0.5 overflow-y-auto">
                        {dayEvents.slice(0, 3).map((data, i) => (
                            <p key={i} title={data.date.getHours() < 12 ? 'Pre-market' : 'Post-market'} className={
                                'px-2 mt-1 font-semibold rounded ' + (
                                    data.name === 'Earnings' ? 'bg-fuchsia-700' :
                                    data.name === 'Dividend Ex' ? 'bg-orange-700' : 'bg-emerald-700'
                                ) +'/75'}
                            >
                                {data.ticker}
                            </p>
                        ))}
                        </div>
                    )}
                </div>
            })}
        </div>
    </div>
}

export default Calendar;