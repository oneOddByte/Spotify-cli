all:
	make token

test:
	curl https://icanhazdadjoke.com

token: 
	curl -X POST -H "Content-Type: application/x-www-form-urlencoded" -H "Authorization: Basic NGZlZjA5YmRiN2M3NGEyNzgxMjljYzgzMDRkYTA5ODY6MDU4NTlhN2I5MjkyNDdiYzkwNjM0ZjdlM2RmNjllNDA=" -d "grant_type=client_credentials" https://accounts.spotify.com/api/token | jq

run: 
	python main.py
