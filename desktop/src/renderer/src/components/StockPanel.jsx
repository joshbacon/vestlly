function StockPanel({ stock }) {
    const meta = stock.meta;
    const data = stock.history[stock.history.length-1];
    return <div className="w-full px-3 bg-mist-950/50 overflow-hidden">
        <p className='text-sm'>{meta.longName} - {meta.exchange}</p>
        <div className='py-3 grid grid-cols-4 gap-x-11 gap-y-2'>
            <div className='flex justify-between place-items-center border-b border-dashed border-teal-700'>
                <p className='font-extralight text-sm text-left'>Forward P/E:</p>
                <p className='font-medium text-sm text-right'>{data.forwardPE != null ? data.forwardPE.toFixed(2) : 'none'}</p>
            </div>
            <div className='flex justify-between place-items-center border-b border-dashed border-teal-700 pb-1'>
                <p className='font-extralight text-sm text-left'>PEG:</p>
                <p className='font-medium text-sm text-right'>{data.pegRatio != null ? data.pegRatio.toFixed(2) : 'none'}</p>
            </div>
            <div className='flex justify-between place-items-center border-b border-dashed border-teal-700 pb-1'>
                <p className='font-extralight text-sm text-left'>50 Day Avg:</p>
                <p className='font-medium text-sm text-right'>{data.fiftyDayAverage != null ? '$'+data.fiftyDayAverage.toFixed(2) : 'none'}</p>
            </div>
            <div className='flex justify-between place-items-center border-b border-dashed border-teal-700 pb-1'>
                <p className='font-extralight text-sm text-left'>Dividend Rate:</p>
                <p className='font-medium text-sm text-right'>{data.dividendRate != null ? '$'+data.dividendRate.toFixed(2) : 'none'}</p>
            </div>
            <div className='flex justify-between place-items-center border-b border-dashed border-teal-700 pb-1'>
                <p className='font-extralight text-sm text-left'>Trainling P/E:</p>
                <p className='font-medium text-sm text-right'>{data.trailingPE != null ? data.trailingPE.toFixed(2) : 'none'}</p>
            </div>
            <div className='flex justify-between place-items-center border-b border-dashed border-teal-700 pb-1'>
                <p className='font-extralight text-sm text-left'>P/S:</p>
                <p className='font-medium text-sm text-right'>{data.priceToSalesTrailing12Months != null ? data.priceToSalesTrailing12Months.toFixed(2) : ''}</p>
            </div>
            <div className='flex justify-between place-items-center border-b border-dashed border-teal-700 pb-1'>
                <p className='font-extralight text-sm text-left'>200 Day Avg:</p>
                <p className='font-medium text-sm text-right'>{data.twoHundredDayAverage != null ? '$'+data.twoHundredDayAverage.toFixed(2) : 'none'}</p>
            </div>
            <div className='flex justify-between place-items-center border-b border-dashed border-teal-700 pb-1'>
                <p className='font-extralight text-sm text-left'>Dividend Yield:</p>
                <p className='font-medium text-sm text-right'>{data.dividendYield != null ? data.dividendYield.toFixed(2)+'%' : 'none'}</p>
            </div>
            <div className='flex justify-between place-items-center border-b border-dashed border-teal-700 pb-1'>
                <p className='font-extralight text-sm text-left'>Short Ratio:</p>
                <p className='font-medium text-sm text-right'>{data.shortRatio != null ? data.shortRatio.toFixed(2) : 'none'}</p>
            </div>
            <div className='flex justify-between place-items-center border-b border-dashed border-teal-700 pb-1'>
                <p className='font-extralight text-sm text-left'>P/B:</p>
                <p className='font-medium text-sm text-right'>{data.priceToBook != null ? data.priceToBook.toFixed(2) : 'none'}</p>
            </div>
            <div className='flex justify-between place-items-center border-b border-dashed border-teal-700 pb-1'>
                <p className='font-extralight text-sm text-left'>52 Week Range:</p>
                <p className='font-medium text-sm text-right'>{data.fiftyTwoWeekLow != null ? '$'+data.fiftyTwoWeekLow.toFixed(2) : ''} - {data.fiftyTwoWeekHigh != null ? '$'+data.fiftyTwoWeekHigh.toFixed(2) : ''}</p>
            </div>
            <div className='flex justify-between place-items-center border-b border-dashed border-teal-700 pb-1'>
                <p className='font-extralight text-sm text-left'>Dividend Payout Ratio:</p>
                <p className='font-medium text-sm text-right'>{data.payoutRatio != null ? data.payoutRatio.toFixed(2)+'%' : 'none'}</p>
            </div>
            <div className='flex justify-between place-items-center border-b border-dashed border-teal-700 pb-1'>
                <p className='font-extralight text-sm text-left'>Forward EPS:</p>
                <p className='font-medium text-sm text-right'>{data.epsForward != null ? data.epsForward.toFixed(2) : 'none'}</p>
            </div>
            <div className='flex justify-between place-items-center border-b border-dashed border-teal-700 pb-1'>
                <p className='font-extralight text-sm text-left'>EPS:</p>
                <p className='font-medium text-sm text-right'>{data.epsCurrentYear != null ? data.epsCurrentYear.toFixed(2) : 'none'}</p>
            </div>
            <div className='flex justify-between place-items-center border-b border-dashed border-teal-700 pb-1'>
                <p className='font-extralight text-sm text-left'>Analyst:</p>
                <p className='font-medium text-sm text-right'>{data.averageAnalystRating != null ? data.averageAnalystRating : 'none'}</p>
            </div>
            <div className='flex justify-between place-items-center border-b border-dashed border-teal-700 pb-1'>
                <p className='font-extralight text-sm text-left'>Book Value:</p>
                <p className='font-medium text-sm text-right'>{data.bookValue != null ? '$'+data.bookValue.toFixed(2) : 'none'}</p>
            </div>
            <div className='flex justify-between place-items-center border-b border-dashed border-teal-700 pb-1'>
                <p className='font-extralight text-sm text-left'>RoE:</p>
                <p className='font-medium text-sm text-right'>{data.returnOnEquity != null ? (data.returnOnEquity*100).toFixed(2)+'%' : 'none'}</p>
            </div>
            <div className='flex justify-between place-items-center border-b border-dashed border-teal-700 pb-1'>
                <p className='font-extralight text-sm text-left'>D/E:</p>
                <p className='font-medium text-sm text-right'>{data.debtToEquity != null ? data.debtToEquity.toFixed(2) : 'none'}</p>
            </div>
            <div className='flex justify-between place-items-center border-b border-dashed border-teal-700 pb-1'>
                <p className='font-extralight text-sm text-left'>Target Range:</p>
                <p className='font-medium text-sm text-right'>{data.targetLowPrice != null ? '$'+data.targetLowPrice.toFixed(2) : ''} - {data.targetHighPrice != null ? '$'+data.targetHighPrice.toFixed(2) : ''}</p>
            </div>
            <div className='flex justify-between place-items-center border-b border-dashed border-teal-700 pb-1'>
                <p className='font-extralight text-sm text-left'>Beta:</p>
                <p className='font-medium text-sm text-right'>{data.beta != null ? data.beta.toFixed(2) : 'none'}</p>
            </div>
            <div className='flex justify-between place-items-center border-b border-dashed border-teal-700 pb-1'>
                <p className='font-extralight text-sm text-left'>RoA:</p>
                <p className='font-medium text-sm text-right'>{data.returnOnAssets != null ? (data.returnOnAssets*100).toFixed(2)+'%' : 'none'}</p>
            </div>
        </div>
    </div>
}

export default StockPanel;