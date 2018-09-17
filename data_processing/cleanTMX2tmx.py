import sys
import re
import os
import configparser

def cleanStr(tmxStr):
    patterList=[r'&lt;.*?&gt;',r'lt;.*gt;']
    #patterList=[r':?/cs',r'&lt;.+?&gt;',r'/b|B',r':cn?s',r':/fc',r'/span',r':/?fc',r':v',r'&gt;']
    #patterList=[r':?/cs',r'&lt;.*&gt;',r'/b|B',r':cn?s',r':/fc',r'/span',r':/?fc',r':v',r'&lt;:fc \d&gt;',r'&lt;:hmk \d{1,3}&gt;',r'&lt;:t&gt;',r'&gt;']
    #escapeStrList=['&lt;/em&gt;','&lt;:/fc&gt;','&lt;:gt','&lt;:/cns','&lt;/a&','&lt;','&quot;','&amp;','gt;','&apos;',':crmk','imk']
    escapeStrList=['&lt;:/cns','&lt;/a&','&lt;','&quot;','&amp;','&gt;','gt;','&apos;',':crmk','imk','lt;']
    for patter in patterList:
        tmxStr=re.sub(patter,'',tmxStr)
    for escapeStr in escapeStrList:
        tmxStr=tmxStr.replace(escapeStr,'')
    return tmxStr
    
def cleanTmx(arg):
    # python ..\cleanTmx.py de tmxFilePath enFilePath forgeinFilePath
    # arg[1] can be 'de' or 'none' . Means cleaned the german from en-us segment,if the foregn language isn't german 
    # it's better to be set as none 
    # to be converted TMX file Path : arg[2]
    # arg[3] means en file path
    # arg[4] means forgein file path
    if arg[1]=="batch":
        batchCleanTmx(arg[3], arg[4], arg[5], arg[2])
        return
    try:
        file=open(arg[2],'r', encoding='utf-8')
        fileStr=file.read()
        cleanUT=re.sub(r'<ut>.*?</ut>','',fileStr)
        cleanUT=re.sub(r'<bpt.*?/bpt>', '', cleanUT)
        cleanUT=re.sub(r'<ept.*?/ept>', '', cleanUT)
        cleanUT=re.sub(r'<ph.*?/ph>', '', cleanUT)
        cleanUT=re.sub(r'<it.*?/it>', '', cleanUT)
        cleanExtra=cleanStr(cleanUT)
        segList=re.findall(r'<seg>.*</seg>',cleanExtra)
        #flag=True
        enStr=''
        foreignStr=''
        #If some translation is empty , this version would cause problem 
        """
        for seg in segList:
            cleaned=seg.replace(r'<seg>','')
            cleaned=cleaned.replace(r'</seg>','')
            cleaned=cleaned.strip()
            #if cleaned[:0]=='!' or cleaned[:1]=='$$':
                #cleaned=''
            if len(cleaned)!=0:
                cleaned+='\n'
            if flag==True:
                enStr+=cleaned
                flag=False
            else:
                foreignStr+=cleaned
                flag=True
        """
        i=0
        while (i+1)<len(segList):
            seg1=segList[i].replace(r'<seg>','')
            seg1=seg1.replace(r'</seg>','')
            seg1=seg1.strip()
            seg1=cleanDirtEn(arg[1], seg1)
            seg2=segList[i+1].replace(r'<seg>','')
            seg2=seg2.replace(r'</seg>','')
            seg2=seg2.strip()
            '''
            if len(seg1)>0:                
                if seg1[0]==':' or seg1[0]=='*' or seg1[0]==';':
                    seg1=seg1[1:len(seg1)-1]
                else:
                    pass
                
            if len(seg2)>0:
                if seg2[0]==':' or seg2[0]=='*' or seg2[0]==';':
                    seg2=seg2[1:len(seg2)-1]
                else:
                    pass  
            '''
            patterList=[r'\(\)',r'=',r'_']
            '''                
            if len(seg1)>0:
                lenSeg1=len(re.findall(r'[.,$_-]',seg1[0]))
            if len(seg2)>0:
                lenSeg2=len(re.findall(r'[.,$_-]',seg2[0]))   
            
            if seg1=='' or lenSeg1!=0 or seg2=='' or lenSeg2!=0:
                pass
            '''
            if len(seg1)>0:
                lenSeg1=len(re.findall(r'[.,$_-]',seg1[0]))
                if lenSeg1!=0:
                    pass
                else:
                    for patter in patterList:
                        lenSeg1=len(re.findall(patter,seg1))
                        if lenSeg1!=0:
                            break
            if seg1=='' or lenSeg1!=0 or seg2=='':
                pass
            else:
                seg1=seg1.strip()+'\n'
                seg2=seg2.strip()+'\n'
                enStr+=seg1
                foreignStr+=seg2
            i+=2
        #if(len(enStr)!=0):
            #enStr=enStr[0:len(enStr)-1]
        #if(len(foreignStr)!=0):
            #foreignStr=foreignStr[0:len(foreignStr)-1]
        enFile=open(arg[3],'a', encoding='utf-8')
        enFile.write(enStr)
        enFile.close()
        # foreignFile=open(arg[4],'a')
        # foreignFile.write(foreignStr)
        # foreignFile.close()
    except Exception as e:
        print(e)
def cleanDirtEn(language,segment):
    #clean the en segment to confirm the segment is pure En.
    #language could be 'de' and 'none' I have not finished this function completely
    if language=="none":
        return segment
    else:
        copyOfSeg=segment
        #read config
        scriptPath=os.path.split(os.path.realpath(__file__))[0]
        iniPath=scriptPath+'/cleanTMX.ini'
        config=configparser.ConfigParser()
        config.read(iniPath)
        #initial special character list and so on
        slashList=eval(config.get('languages','slash'))
        englishList=eval(config.get('languages','english'))              
        languageList=eval(config.get('others', 'languageList')) 
        judgedLang=eval(config.get('languages',language))
        if language=='de':# I have not finish all the commonWords in every language
            commonWordsList= eval(config.get('languages',language+'CommonWords'))
        else:
            commonWordsList=[]
        decodedSegment=copyOfSeg.decode('utf-8-sig')
        #check if there's specail character in the segment to judge if en is dirty
        for alph in decodedSegment:
            if alph in englishList or alph in slashList or  (alph>=u'\x80' and alph<=u'\x9f') or (alph>=u'\xa0' and alph<=u'\xbf') or (alph>=u'\u2000' and alph<=u'\u206f'):
                pass
            elif language in languageList:
                if alph in judgedLang:
                    pass
                else:
                    segment=''
        if len(segment)!=0:            
            wordsInSegment=re.sub(r'[,.]','',copyOfSeg).lower().split(' ')
            for word in wordsInSegment:
                if word in commonWordsList:
                    segment=''
                    break
        return segment

def batchCleanTmx(path,  spath, tpath, lan="none"):
    filelist=[]
    for root, dirs, files in os.walk(path):
        del dirs
        for name in files:
            if name.endswith('.tmx'):
                filelist.append(os.path.join(root, name))
    for f in filelist:
        cleanTmx(['', lan, f, spath, tpath])
    

    

       
def test():
    patterList=[r'&lt;:fc \d&gt;',r'&lt;:hmk \d{1,3}&gt;',r'&lt;:t&gt;']
    #escapeStrList=['&lt;/em&gt;','&lt;:/fc&gt;','&lt;:gt','&lt;:/cns','&lt;/a&','&lt;','&quot;','&gt;','&amp;']
    file=open('d:\\test\\test.tmx')
    fileStr=file.read()
    cleanUT=re.sub(r'<ut>.+?</ut>','',fileStr)
    cleanUT=re.sub(patterList[0],'',cleanUT)
    #for patter in patterList:
    #
if __name__=="__main__":
    cleanTmx(sys.argv)
    
