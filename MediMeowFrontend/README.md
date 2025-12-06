# MediMeow Frontend (Doctor Workstation)

This is the Vue 3 frontend for the MediMeow Doctor Workstation.

## Setup

1. **Install Dependencies**
   ```bash
   npm install
   ```

2. **Run Development Server**
   ```bash
   npm run dev
   ```

3. **Build for Production**
   ```bash
   npm run build
   ```

## Configuration

- **API Proxy**: Configured in `vite.config.js` to proxy `/api` to `http://localhost:8000`.
- **Port**: Default Vite port (usually 5173).

## Features

- **Doctor Login**: Authenticate using doctor credentials.
- **Patient Queue**: View list of assigned patients (fetched from backend).
- **Patient Detail**: View patient summary, AI analysis, and submit diagnosis.
- **Responsive UI**: Built with Tailwind CSS.

## Project Structure

- `src/views`: Page components (Login, Dashboard, Detailed Patient View).
- `src/components`: Reusable layout components (Sidebar, TopBar).
- `src/stores`: State management (Auth, Patient) using Pinia.
- `src/api`: Axios setup for API communication.
