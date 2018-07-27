# minikube start
docker build -t neuralknight .
# kubectl apply -f application/deployment.yaml
# kubectl describe deployment nginx-deployment
docker run --rm --label=neuralknight -it -p 8080:80 neuralknight
