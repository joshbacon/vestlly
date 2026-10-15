function ErrorPage({ message }) {
    return <div className="flex flex-col justify-center place-items-center w-full h-screen bg-mist-950">
        <h1 className="text-red-700 font-bold text-2xl">ERROR</h1>
        <p>{message}</p>
    </div>
}

export default ErrorPage;