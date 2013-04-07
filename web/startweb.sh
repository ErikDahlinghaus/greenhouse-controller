#!/bin/bash


cd /home/host/web
webstart='python controller.py'
$webstart >weblog 2>&1
