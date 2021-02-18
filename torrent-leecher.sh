#!/bin/bash

aria2c \
	--enable-rpc \
	--conf-path=/app/tobrot/aria2/aria2.conf &
python3 -m tobrot
