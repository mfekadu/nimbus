#!/usr/bin/env python3

from pydrive.auth import GoogleAuth

gauth = GoogleAuth()
# Create local webserver and auto handles authentication.
# gauth.CommandLineAuth()
gauth.LocalWebserverAuth(port_numbers=[8080])

print("authenticated.")