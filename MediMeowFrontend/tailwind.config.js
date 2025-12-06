/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{vue,js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                primary: '#2C7DB1',
                secondary: '#34495E',
                accent: '#F39C12',
                danger: '#E74C3C',
                success: '#27AE60',
                background: '#ECF0F1',
            }
        },
    },
    plugins: [],
}
