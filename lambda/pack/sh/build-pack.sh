#!/bin/bash -x
ENV=/home/$USER/packs/$1

pushd $ENV
mkdir build
for f in $(cat $ENV/inotifywait.list | sort | uniq); do
  if [ -f $f ]; then
    # Note this cuts the first 31 chars, which is heavily dependant on your local setting
    REL=$(dirname $f | cut -c 31-)
    mkdir -p build/$REL
    cp $f build/$REL
  fi
done

pushd $ENV/lib/python2.7/site-packages/
find . -name "*.py" | cut -c 3- > $ENV/pydep.list
popd

for f in $(cat $ENV/pydep.list); do
  cp "$ENV/lib/python2.7/site-packages/$f" "$ENV/build/$f" 2>/dev/null
done
popd

