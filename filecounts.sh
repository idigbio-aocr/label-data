#!/usr/bin/env bash

for i in ent herb lichens; do
    echo "--------";
    echo $i;
    echo "--------";
    echo -n "$i/gold/inputs "; ls $i/gold/inputs | wc -l;
    echo -n "$i/gold/ocr "; ls $i/gold/ocr | wc -l;
    echo -n "$i/gold/parsed "; ls $i/gold/parsed | wc -l;
    echo -n "$i/silver/ocr "; ls $i/silver/ocr | wc -l;
    echo -n "$i/silver/parsed "; ls $i/silver/parsed | wc -l;
done