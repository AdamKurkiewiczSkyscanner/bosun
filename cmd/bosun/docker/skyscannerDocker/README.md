In order to build a docker container with Skyscanner's version of Bosun run `buildContainer.py` as root. The script runs in python2 and assumes that executable `docker` is in your $PATH.

While the script executes it will output to stdout information about actions that are executed. After the script is finished, the last line of stdout should be of the form:

`Successfully built <hash-id>`

Copy the hash-id and run in your shell:

`sudo docker run -p 8070:8070 <hash-id>`
