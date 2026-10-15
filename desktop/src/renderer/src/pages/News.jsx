import icon from '../../../../resources/icon.png?asset';

import { RotateCw } from 'lucide-react';
import { useEffect, useState } from "react";

function NewsPage() {

    const [ articles, setArticles ] = useState([]);
    const [ searchTerm, setSearchTerm ] = useState("");

    const fetchArticles = async (input) => {
        const res = await fetch(`http://localhost:8000/api/news/${input}`);
        if (!res.ok) throw new Error("Failed to fetch stock data");
        return res.json();
    }

    const updateArticles = async (input="BMO.TO") => {
        const newArticles = await fetchArticles(input);
        if (newArticles.articles.length > 0) {
            setArticles(newArticles.articles);
        }
    }

    useEffect(() => {
        updateArticles();
    }, []);

	useEffect(() => {
        if (searchTerm.trim().length < 2) {
            return;
        }
		const debounceTimer = setTimeout(async () => {
            const data = await updateArticles(searchTerm);
		}, 1000);

		return () => clearTimeout(debounceTimer);
	}, [searchTerm]);

    const handleArticleClick = (link) => {
        console.log(link);
        window.electronAPI.openExternal(link);
    };

    return <div className="overflow-y-auto">
        <div className='p-3 flex justify-between place-items-center'>
            <input
                type="text"
                value={searchTerm}
                placeholder="Search ticker"
                autoFocus="true"
                className="bg-mist-800 rounded-lg py-1 px-2 min-w-60 outline-0"
                onChange={({ target }) => setSearchTerm(target.value)}
            />
            <button
                className='cursor-pointer'
                onClick={updateArticles}
                title='Refresh'
            >
                <RotateCw size={28} color="#00786f"/>
            </button>
        </div>
        {
            articles.map(({ content }) => {
                return <div
                    key={content.id}
                    className='m-5 flex bg-mist-900'
                >
                    <img
                        className='max-w-xs aspect-square rounded-sm'
                        src={content.thumbnail != null ? content.thumbnail.originalUrl : icon}
                        alt="no thumbnail"
                    />
                    <div className='w-full p-3 flex flex-col gap-2'>
                        <h1 className='text-lg font-bold'>{content.title}</h1>
                        <p>{content.summary}</p>
                        { content.clickThroughUrl != null ?
                            <p
                                onClick={() => {handleArticleClick(content.clickThroughUrl.url)}}
                                className="cursor-pointer text-teal-600 hover:text-teal-500"
                            >
                                Read More...
                          </p> :
                          <></> }
                    </div>
                </div>
            })
        }
    </div>
}

export default NewsPage;