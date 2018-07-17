FROM golang:alpine

EXPOSE 80

RUN apk add --no-cache git

WORKDIR /go/src/github.com/neuralknight/neuralknight
COPY . .

RUN go get -d -v ./...
RUN go install -v ./...

CMD ["neuralknight"]
