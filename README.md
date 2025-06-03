# My Dashboard
Backend data collection from different data sources

## Integrated Sources
- Ticktick (unofficial Api):
  - Tasks
  - Habits
  - Focus Times
- Sanitas Smart Scale (web):
  - Weight data
- Budgetbakers Wallet (web):
  - Account balance
  - Transactions


# How to Use
The repository contains multiple Dockerfiles, each dedicated to one data source.
To use, you only need to build, push and publish the images to gloud run.


### Installation

1. Set environment variables in `.env`:
   - `FIREBASE_REALTIME_DB_URL`
   - `[service]_EMAIL` & `[service]_PASSWORD` for TICKTICK, SANITAS & BUDGETBAKERS
2. Authenticate Docker: `make auth-docker`
3. Build docker images: `make build`
4. Push images to gcloud artifacts: `make push`
5. Deploy the image: `make deploy`

_All commands can be executed for a specific service using_ ` SERVICES=[service]` _(lowercase)_

### Required Tools
- make (windows installable via `choco install make` with priviledges)
- gcloud sdk
- docker
