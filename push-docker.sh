# build all dockerfiles
docker build -t us-west1-docker.pkg.dev/ostoll/my-data/sanitas:latest -f ./Dockerfile-Sanitas .
docker build -t us-west1-docker.pkg.dev/ostoll/my-data/diaro:latest -f ./Dockerfile-Diaro .
docker build -t us-west1-docker.pkg.dev/ostoll/my-data/budgetbakers:latest -f ./Dockerfile-Budgetbakers .
docker build -t us-west1-docker.pkg.dev/ostoll/my-data/ticktick_habits:latest -f ./Dockerfile-TicktickHabits .
docker build -t us-west1-docker.pkg.dev/ostoll/my-data/ticktick_tasks:latest -f ./Dockerfile-TicktickTasks .
docker build -t us-west1-docker.pkg.dev/ostoll/my-data/ticktick_focus:latest -f ./Dockerfile-TicktickFocus .


# run dockerfiles
docker run -p 8080:8080 us-west1-docker.pkg.dev/ostoll/my-data/sanitas:latest
docker run -p 8080:8080 us-west1-docker.pkg.dev/ostoll/my-data/diaro:latest
docker run -p 8080:8080 us-west1-docker.pkg.dev/ostoll/my-data/budgetbakers:latest
docker run -p 8080:8080 us-west1-docker.pkg.dev/ostoll/my-data/ticktick_habits:latest
docker run -p 8080:8080 us-west1-docker.pkg.dev/ostoll/my-data/ticktick_tasks:latest
docker run -p 8080:8080 us-west1-docker.pkg.dev/ostoll/my-data/ticktick_focus:latest


# push all dockerfiles
docker push us-west1-docker.pkg.dev/ostoll/my-data/sanitas
docker push us-west1-docker.pkg.dev/ostoll/my-data/diaro
docker push us-west1-docker.pkg.dev/ostoll/my-data/budgetbakers
docker push us-west1-docker.pkg.dev/ostoll/my-data/ticktick_habits
docker push us-west1-docker.pkg.dev/ostoll/my-data/ticktick_tasks
docker push us-west1-docker.pkg.dev/ostoll/my-data/ticktick_focus


# deploy all dockerfiles
gcloud run deploy sanitas-scraper  --allow-unauthenticated --image=us-west1-docker.pkg.dev/ostoll/my-data/sanitas:latest --region=us-west1 --project=ostoll  --memory 1Gi
gcloud run deploy diaro-scraper  --allow-unauthenticated --image=us-west1-docker.pkg.dev/ostoll/my-data/diaro:latest --region=us-west1 --project=ostoll --memory 1Gi
gcloud run deploy budgetbakers-scraper  --allow-unauthenticated --image=us-west1-docker.pkg.dev/ostoll/my-data/budgetbakers:latest --region=us-west1 --project=ostoll --memory 1Gi
gcloud run deploy ticktick-habits-scraper  --allow-unauthenticated --image=us-west1-docker.pkg.dev/ostoll/my-data/ticktick_habits:latest --region=us-west1 --project=ostoll --memory 1Gi
gcloud run deploy ticktick-tasks-scraper  --allow-unauthenticated --image=us-west1-docker.pkg.dev/ostoll/my-data/ticktick_tasks:latest --region=us-west1 --project=ostoll --memory 1Gi
gcloud run deploy ticktick-focus-scraper  --allow-unauthenticated --image=us-west1-docker.pkg.dev/ostoll/my-data/ticktick_focus:latest --region=us-west1 --project=ostoll --memory 1Gi


