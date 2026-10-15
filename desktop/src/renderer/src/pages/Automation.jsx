function AutomationPage() {
    return <div className="p-10">
        <div>this page allows you to connect to brokerage accounts through snaptrade</div>
        <div>it also allows you to setup automations:</div>
        <ul>
            <li>Havea an account select/add panel on the left (like watchlist but for accounts)</li>
            <li>Once one is selected</li>
            <ol className="list-decimal pt-3">
                <li>select which watchlists to include in the training</li>
                <li>be able to re-train the evaluation function based on the stocks in chosen watchlists</li>
                * have a warning message pop up if the stocklist is changed but the model isn't re-trained yet
                <li>be able to change variables like lot size</li>
                <li>be able to turn the automation on and off</li>
                <li>also show the account performance and other data</li>
            </ol>
        </ul>
    </div>
}

export default AutomationPage;