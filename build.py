# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals
import sys
from subprocess import call
import shutil
from unipath import Path
import os
BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__)))


def osx():
    print("running osx specifics")
    if not os.path.exists(BASE_DIR.child("machinery-skeleton").child("skeleton").child("tmp")):
        os.mkdir(BASE_DIR.child("machinery-skeleton").child("skeleton").child("tmp"))

    call(["cp", "-R", "machinery-skeleton/skeleton/osx/machinery.app", "machinery-skeleton/skeleton/tmp"])
    call(["mkdir", "-p", "machinery-skeleton/skeleton/tmp/machinery.app/Contents/Resources/app/"])
    call(["cp", "package.json", "machinery-skeleton/skeleton/tmp/machinery.app/Contents/Resources/app/"])
    call(["cp", "main.js", "machinery-skeleton/skeleton/tmp/machinery.app/Contents/Resources/app/"])
    call(["cp", "main.html", "machinery-skeleton/skeleton/tmp/machinery.app/Contents/Resources/app/"])
    call(["cp", "-R", "dist/", "machinery-skeleton/skeleton/tmp/machinery.app/Contents/Resources/app/"])

    call(["rm", "-rf", "release/osx/machinery_latest.dmg"])
    call(["appdmg", "machinery-skeleton/skeleton/osx/appdmg.json", "release/osx/machinery_latest.dmg"])


def win():
    print("running win specifics")
    call(["mkdir", "-p", BASE_DIR.child("machinery-skeleton").child("skeleton").child("tmp")])
    shutil.copytree(BASE_DIR.child("machinery-skeleton").child("skeleton").child("win"),
                    BASE_DIR.child("machinery-skeleton").child("skeleton").child("tmp").child("machinery"))
    call(["mkdir", "-p", "machinery-skeleton\\skeleton\\tmp\\machinery\\resources\\app\\"])

    call(["cp", "package.json", "machinery-skeleton\\skeleton\\tmp\\machinery\\resources\\app\\"])
    call(["cp", "main.js", "machinery-skeleton\\skeleton\\tmp\\machinery\\resources\\app\\"])
    call(["cp", "main.html", "machinery-skeleton\\skeleton\\tmp\\machinery\\resources\\app\\"])
    shutil.copytree("dist", "machinery-skeleton\\skeleton\\tmp\\machinery\\resources\\app\\dist")
    shutil.move("machinery-skeleton\\skeleton\\tmp\\machinery\\resources\\app\\dist\\machinery\\machinery",
                "machinery-skeleton\\skeleton\\tmp\\machinery\\resources\\app\\dist\\machinery\\machinery.exe")
    call(["7z", "a", "-tzip", "release\\win\\machinery_latest.zip", ".\\machinery-skeleton\\skeleton\\tmp\\machinery"])

def linux():
    print("running linux specifics")


def build():
    print("building ...")
    shutil.rmtree(BASE_DIR.child("dist"), ignore_errors=True)
    shutil.rmtree(BASE_DIR.child("bin"), ignore_errors=True)
    shutil.rmtree(BASE_DIR.child("machinery-skeleton").child("skeleton").child("tmp"), ignore_errors=True)
    call(["pyinstaller", "--name", "machinery", "--onedir", 'machinery.spec'])


if __name__ == "__main__":
    args = sys.argv
    if len(args) > 2 or len(args) == 1:
        print("usage: python build.py [platform] ")
        exit()

    platform = args[1]

    if platform not in ["osx", "win", "linux"]:
        print("Platform has to be osx, win or linux")
        exit()

    build()
    locals()[platform]()