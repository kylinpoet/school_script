rem 执行改批处理前先要目录下创建font_properties文件 
 echo fontyp 0 0 0 0 0 >font_properties
echo Run Tesseract for Training.. 

tesseract langyp.fontyp.exp0.tif langyp.fontyp.exp0 -l eng -psm 7 nobatch box.train 
 
echo Compute the Character Set.. 
unicharset_extractor.exe langyp.fontyp.exp0 
mftraining -F font_properties -U unicharset -O langyp.unicharset langyp.fontyp.exp0.tr 


echo Clustering.. 
cntraining.exe langyp.fontyp.exp0.tr

echo Rename Files.. 
rename normproto langyp.normproto 
rename inttemp langyp.inttemp 
rename pffmtable langyp.pffmtable 
rename shapetable langyp.shapetable  

echo Create Tessdata.. 
combine_tessdata.exe langyp. 
echo. & pause