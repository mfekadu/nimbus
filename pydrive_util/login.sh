# this script will show you a URL to login with Google
#
# after 10 seconds, this same script will call `wget localhost:8080`
#
# that should then tell pydrive (within the `gauth.py` script) to authenticate.
#
# if something goes wrong,
# try to do `wget <the last URL that your browser arrived at after Authenticating>
#
# the credentials get saved into `save_cred.json` so you only need do this once.

L1="from urllib.request import urlopen"
L2="url=input(\"redirect_url (localhost..code=...): \")"
L3="\n"
L4="try:"
L5="     urlopen(url)"
L6="except BrokenPipeError:"
L7="     pass"
L8="exit(0)"
echo "$L1\n$L2\n$L3\n$L4\n$L5\n$L6\n$L7\n$L8\n" >tmp.py

./gauth.py &
sleep 3
echo
echo
python3 tmp.py

rm tmp.py
