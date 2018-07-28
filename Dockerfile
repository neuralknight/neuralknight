FROM golang:alpine

EXPOSE 80

RUN apk add --no-cache gcc git musl-dev

WORKDIR /go/src/github.com/neuralknight/neuralknight
COPY . .

RUN go get -d -v ./...
RUN go install -v ./...
RUN go test -v ./...

CMD ["neuralknight", "--port", "80"]
