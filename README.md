# My Dashboard
Aggregates and synchronizes personal data from various services into a central backend, and displayes them via a browser-integrated dashboard frontend.

## Backend
The repository contains multiple Dockerfiles, each dedicated to one data source.
Each data source has a dedicated Docker container for scheduled ingestion and transformation. Deployment targets Google Cloud Run.
To use, you only need to build, push and publish the images to gloud run.

### Integrated Data Sources
- Ticktick (unofficial Api):
  - Tasks
  - Habits
  - Focus Times
- Sanitas Smart Scale (web):
  - Weight data
- Budgetbakers Wallet (web):
  - Account balance
  - Transactions

### Prerequisites
- make 
- docker
- gcloud CLI
- Google Artifact Registry configured

### Setup

1. Set environment variables in `.env`:
   - `FIREBASE_REALTIME_DB_URL`
   - `[service]_EMAIL` & `[service]_PASSWORD` for services TICKTICK, SANITAS & BUDGETBAKERS
2. Authenticate Docker:
   `make auth-docker`
3. Build docker images:
   `make build`
4. Push images to gcloud artifacts:
   `make push`
5. Deploy the image:
   `make deploy`

_All commands can be executed for a specific service using_ ` SERVICES=[service]` _(lowercase)_

## Frontend

The frontend provides a unified interface for visualizing personal data aggregated by the backend services.
The Dashboard shows an overview of all relevant metrics as a visualized percentage value depending on customizable goal values. 
For habits, the goal is depending on the set habit goals in TickTick.

### Installation

### Features

- Task, habit, and focus time overview from TickTick
- Expense and account balance tracking from BudgetBakers
- Time-series plots of weight from Sanitas (planned)
- Daily summaries and historical trends across sources

### Technology Stack

- React with Vite
- Tailwind CSS for styling
- Firebase Realtime Database as the primary data store
- Chart.js for visualizations

### Setup & Local Development

1. Fill `.env` and configure Firebase keys
2. Install dependencies:  
   `npm install`
3. Start development server:  
   `npm run dev`
4. Load browser extension via `chrome://extensions/` -> `Load unpacked` -> Select `frontend` directory



