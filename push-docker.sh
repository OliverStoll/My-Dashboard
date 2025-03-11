# build all dockerfiles

echo "Building Sanitas..."
docker build -t us-west1-docker.pkg.dev/notion-api-sync/my-data/sanitas_scraper:latest -f ./Dockerfile-Sanitas .

echo "Building Diaro..."
docker build -t us-west1-docker.pkg.dev/notion-api-sync/my-data/diaro_scraper:latest -f ./Dockerfile-Diaro .

echo "Building Budgetbakers..."
docker build -t us-west1-docker.pkg.dev/notion-api-sync/my-data/budgetbakers_scraper:latest -f ./Dockerfile-BudgetBakers .

echo "Building TickTick Habits..."
docker build -t us-west1-docker.pkg.dev/notion-api-sync/my-data/ticktick_habits_scraper:latest -f ./Dockerfile-TickTickHabits .




# push all dockerfiles
echo "Pushing Sanitas..."
docker push us-west1-docker.pkg.dev/notion-api-sync/my-data/sanitas_scraper

echo "Pushing Diaro..."
docker push us-west1-docker.pkg.dev/notion-api-sync/my-data/diaro_scraper

echo "Pushing Budgetbakers..."
docker push us-west1-docker.pkg.dev/notion-api-sync/my-data/budgetbakers_scraper

echo "Pushing TickTick Habits..."
docker push us-west1-docker.pkg.dev/notion-api-sync/my-data/ticktick_habits_scraper


# deploy all dockerfiles
echo "Deploying Sanitas..."
gcloud run deploy sanitas-scraper  --allow-unauthenticated --image=us-west1-docker.pkg.dev/notion-api-sync/my-data/sanitas_scraper:latest --region=us-west1 --project=notion-api-sync  --memory 1Gi

echo "Deploying Diaro..."
gcloud run deploy diaro-scraper  --allow-unauthenticated --image=us-west1-docker.pkg.dev/notion-api-sync/my-data/diaro_scraper:latest --region=us-west1 --project=notion-api-sync --memory 1Gi

echo "Deploying Budgetbakers..."
gcloud run deploy budgetbakers-scraper  --allow-unauthenticated --image=us-west1-docker.pkg.dev/notion-api-sync/my-data/budgetbakers_scraper:latest --region=us-west1 --project=notion-api-sync --memory 1Gi

echo "Deploying TickTick Habits..."
gcloud run deploy ticktick-habits-scraper  --allow-unauthenticated --image=us-west1-docker.pkg.dev/notion-api-sync/my-data/ticktick_habits_scraper:latest --region=us-west1 --project=notion-api-sync --memory 1Gi
