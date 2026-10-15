import icon from '../../../../resources/icon.png?asset';

function LoadingPage({ progress }) {
    const pct = progress.total > 0
        ? Math.round((progress.completed / progress.total) * 100)
        : 0;

    return <div className="w-full h-screen bg-mist-950 flex flex-col justify-center place-items-center gap-3">
        <img src={icon} width={150} height={150} alt="" />
        <h1>LOADING...</h1>
        <div className="min-w-80 h-2 bg-mist-800 rounded-2xl overflow-hidden">
            <div className="h-full bg-teal-800 transition-[width] duration-150 ease-out" style={{ width: `${pct}%` }} />
        </div>
    </div>
}

export default LoadingPage;