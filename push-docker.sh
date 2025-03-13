# build all dockerfiles
docker build -t us-west1-docker.pkg.dev/notion-api-sync/my-data/sanitas_scraper:latest -f ./Dockerfile-Sanitas .
docker build -t us-west1-docker.pkg.dev/notion-api-sync/my-data/diaro_scraper:latest -f ./Dockerfile-Diaro .
docker build -t us-west1-docker.pkg.dev/notion-api-sync/my-data/budgetbakers_scraper:latest -f ./Dockerfile-Budgetbakers .
docker build -t us-west1-docker.pkg.dev/notion-api-sync/my-data/ticktick_habits_scraper:latest -f ./Dockerfile-TicktickHabits .
docker build -t us-west1-docker.pkg.dev/notion-api-sync/my-data/ticktick_tasks_scraper:latest -f ./Dockerfile-TicktickTasks .


# run dockerfiles
docker run -p 8080:8080 us-west1-docker.pkg.dev/notion-api-sync/my-data/sanitas_scraper:latest
docker run -p 8080:8080 us-west1-docker.pkg.dev/notion-api-sync/my-data/diaro_scraper:latest
docker run -p 8080:8080 us-west1-docker.pkg.dev/notion-api-sync/my-data/budgetbakers_scraper:latest
docker run -p 8080:8080 us-west1-docker.pkg.dev/notion-api-sync/my-data/ticktick_habits_scraper:latest
docker run -p 8080:8080 us-west1-docker.pkg.dev/notion-api-sync/my-data/ticktick_tasks_scraper:latest


# push all dockerfiles
docker push us-west1-docker.pkg.dev/notion-api-sync/my-data/sanitas_scraper
docker push us-west1-docker.pkg.dev/notion-api-sync/my-data/diaro_scraper
docker push us-west1-docker.pkg.dev/notion-api-sync/my-data/budgetbakers_scraper
docker push us-west1-docker.pkg.dev/notion-api-sync/my-data/ticktick_habits_scraper
docker push us-west1-docker.pkg.dev/notion-api-sync/my-data/ticktick_tasks_scraper


# deploy all dockerfiles
gcloud run deploy sanitas-scraper  --allow-unauthenticated --image=us-west1-docker.pkg.dev/notion-api-sync/my-data/sanitas_scraper:latest --region=us-west1 --project=notion-api-sync  --memory 1Gi
gcloud run deploy diaro-scraper  --allow-unauthenticated --image=us-west1-docker.pkg.dev/notion-api-sync/my-data/diaro_scraper:latest --region=us-west1 --project=notion-api-sync --memory 1Gi
gcloud run deploy budgetbakers-scraper  --allow-unauthenticated --image=us-west1-docker.pkg.dev/notion-api-sync/my-data/budgetbakers_scraper:latest --region=us-west1 --project=notion-api-sync --memory 1Gi
gcloud run deploy ticktick-habits-scraper  --allow-unauthenticated --image=us-west1-docker.pkg.dev/notion-api-sync/my-data/ticktick_habits_scraper:latest --region=us-west1 --project=notion-api-sync --memory 1Gi
gcloud run deploy ticktick-tasks-scraper  --allow-unauthenticated --image=us-west1-docker.pkg.dev/notion-api-sync/my-data/ticktick_tasks_scraper:latest --region=us-west1 --project=notion-api-sync --memory 1Gi



