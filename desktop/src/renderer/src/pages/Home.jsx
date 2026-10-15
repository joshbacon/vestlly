function HomePage() {
    return <div className="flex flex-wrap gap-5 p-10">
      <div>Show the portfolio data here for any connected accounts, have a graph with historic data too if possible (without having to track manually)</div>
      <div className="bg-mist-700 rounded-2xl px-8 py-5">
        <h2 className="text-2xl font-extrabold text-right">
          Frontend MVP
        </h2>
        <ol className="list-decimal pt-3">
          <li>Home Page</li>
          <li className="line-through">Search Page</li>
          <li className="line-through">Watchlists Page</li>
          <li className="line-through">News Page</li>
          <li className="line-through">Calendar Page</li>
          <li >Analysis Page</li>
          <h3 className="text-sm">
            *Want to show the score and weight of each indicator with a total eval score at the top.
          </h3>
          <li>Automation (need the features built out first so I know what is available to edit)</li>
          <li>Memory Management (cache as much as possible and load it all on start)</li>
        </ol>
      </div>
      <div className="bg-mist-700 rounded-2xl px-8 py-5">
        <h2 className="text-2xl font-extrabold text-right">
          API
        </h2>
        <ol className="list-decimal pt-3">
          <li className="line-through">Query yfinance</li>
          <li>Database endpoints</li>
        </ol>
      </div>
      <div className="bg-mist-700 rounded-2xl px-8 py-5">
        <h2 className="text-2xl font-extrabold text-right">
          Database
        </h2>
        <ol className="list-decimal pt-3">
          <li>Ticker lookup cache</li>
          <li>Analysis results</li>
        </ol>
      </div>
      <div className="bg-mist-700 rounded-2xl px-8 py-5">
        <h2 className="text-2xl font-extrabold text-right">
          Algorithm
        </h2>
        <ol className="list-decimal pt-3">
          <li>figure out functions to calculate live indicator values (/evaluation/src/indicators.js)</li>
          * show them on the Analysis page once they're calculated
          <li>figure out how to score the indicators based on the fitting pipline artifact (/evaluation/src/scoring.js)</li>
          <li>figure out how to add more indicators</li>
          * will also need to add them to the python pipeline
        </ol>
      </div>
      <div className="bg-mist-700 rounded-2xl px-8 py-5">
        <h2 className="text-2xl font-extrabold text-right">
          Automation
        </h2>
        <ol className="list-decimal pt-3">
          <li>Figure out how to connect to an account through snaptrade</li>
          <li>Figure out the python pipeline for fitting</li>
          <li>Make frontend for algorithm adjustments and have a way to refit for stocks in included watchlists (Automation page)</li>
          <li>Setup server to execute trades</li>
        </ol>
      </div>
    </div>
}

export default HomePage;