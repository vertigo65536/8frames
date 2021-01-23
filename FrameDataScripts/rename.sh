for i in assets_characterdata_*.json
do
    mv "$i" "`echo $i | sed 's/assets_characterdata_//'`"
done

