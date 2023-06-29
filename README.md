An experience smoother for ESLs who reads "The subtle art of not giving a f*ck"


# How To Serve

1- Download audiobook's mp3 file:
```bash
wget -O "static/the subtle art of not giving a fuck.mp3" "https://free.audiobookslab.com/audio/the-subtle-art-of-not-giving-f.mp3"
```

2- Build docker image and run a container:

```bash
docker build -t audiobook:latest .
docker run -id --name audiobook_server -p 1234:5000 --restart unless-stopped audiobook:latest
```
