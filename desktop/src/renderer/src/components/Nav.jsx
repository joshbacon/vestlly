import { NavLink } from 'react-router-dom';
import { navRoutes } from '../routes';

function NavBar() {
    return <div className="bg-mist-900 flex flex-col font-sans min-w-32">
        <h1 className='p-3 font-bold'>vestlly</h1>
        <div className="flex flex-col">
            {navRoutes.map(({path, label, icon: Icon, end }) => (
                <NavLink
                    key={path}
                    to={path}
                    end={end}
                    className={({ isActive }) =>
                        `flex items-center gap-2 px-3 py-2 rounded-md text-sm transition-colors ${
                            isActive
                            ? 'bg-teal-900 text-white'
                            : 'text-gray-300 hover:bg-teal-900/35 hover:text-white'
                        }`
                    }
                >
                    <Icon size={16} />
                    {label}
                </NavLink>
            ))}
        </div>
    </div>
}

export default NavBar;