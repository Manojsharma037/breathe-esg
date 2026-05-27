import axios from 'axios';

const api = axios.create({
    baseURL: 'https://breathe-esg-backend-zhst.onrender.com/api',
    headers: {
        'Content-Type': 'application/json',
    }
});

export default api;