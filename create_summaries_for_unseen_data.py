# coding=utf-8
# python create_summary_for_unseen_data.py ../dataconversion/GIST_FB/threads/ gistfb.postfeats.norm+selected.out
# python create_summary_for_unseen_data.py ../dataconversion/Viva_forum/samples/20randomthreads 20randomthreads.postfeats.norm+selected.out
# python create_summary_for_unseen_data.py ../dataconversion/GIST_FB/smallsample/ gistfb.postfeats.norm.smallsample+selected.out
# python create_summary_for_unseen_data.py ../dataconversion/Viva_forum/samples/kankerthreads kankerthreads.postfeats.norm+selected.out

# + 1. Read directory
# + 2. Extract post feats
# + 3. Standardize post feats
# + 4. Apply linear model
#  Source: R
#  > setwd("/Users/suzanverberne/Dropbox/Projects/SIDN_PFM/Data")
#  > train=read.table("viva.postfeats.normalized.out.1234",sep="\t",header=TRUE)
#  > trainlm<-glm(nrofvotes ~ abspos + relpos + noresponses + cosinesimwthread + cosinesimwtitle + wordcount + uniquewordcount + ttr + relpunctcount + avgwordlength + avgsentlength + relauthorcountsinthread,data=train)
#  > summary(trainlm)

# + 5. Apply threshold
# Source: R
# > tune=read.table("viva.postfeats.normalized.out.5",sep="\t",header=TRUE)
# > write(predict(trainlm,newdata=tune),file="viva.postfeats.norm.5.tune.out",ncolumns=1)
# --> threshold = 3.72 FIXED, based on tune5
# + 6. Add selection column (1s and 0s)
# + 7. Print to xxx.postfeats.norm+selected.out


import os
import sys
reload(sys)
sys.setdefaultencoding('utf8')
import re
import math
import string
import operator
import functools
import numpy
from scipy.linalg import norm
import time
import xml.etree.ElementTree as ET


rootdir = sys.argv[1]
outfilename = sys.argv[2]


def tokenize(t):
    text = t.lower()
    text = re.sub("\n"," ",text)
    text = re.sub('[^a-zèéeêëûüùôöòóœøîïíàáâäæãåA-Z0-9- \']', "", text)
    wrds = text.split()
    return wrds

caps = "([A-Z])"
prefixes = "(Dhr|Mevr|Dr|Drs|Mr|Ir|Ing)[.]"
suffixes = "(BV|MA|MSc|BSc|BA)"
starters = "(Dhr|Mevr|Dr|Drs|Mr|Ir|Ing)"
acronyms = "([A-Z][.][A-Z][.](?:[A-Z][.])?)"
websites = "[.](com|net|org|io|gov|nl)"

def split_into_sentences(text):
    # adapted from http://stackoverflow.com/questions/4576077/python-split-text-on-sentences
    text = " " + text + "  "
    text = text.replace("\n"," ")
    text = re.sub(prefixes,"\\1<prd>",text)
    text = re.sub(websites,"<prd>\\1",text)
    if "Ph.D" in text: text = text.replace("Ph.D.","Ph<prd>D<prd>")
    text = re.sub("\s" + caps + "[.] "," \\1<prd> ",text)
    text = re.sub(acronyms+" "+starters,"\\1<stop> \\2",text)
    text = re.sub(caps + "[.]" + caps + "[.]" + caps + "[.]","\\1<prd>\\2<prd>\\3<prd>",text)
    text = re.sub(caps + "[.]" + caps + "[.]","\\1<prd>\\2<prd>",text)
    text = re.sub(" "+suffixes+"[.] "+starters," \\1<stop> \\2",text)
    text = re.sub(" "+suffixes+"[.]"," \\1<prd>",text)
    text = re.sub(" " + caps + "[.]"," \\1<prd>",text)
    if "\"" in text: text = text.replace(".\"","\".")
    if "!" in text: text = text.replace("!\"","\"!")
    if "?" in text: text = text.replace("?\"","\"?")
    text = re.sub("([\.\?!]+\)?)","\\1<stop>",text)
    if "<stop>" not in text:
        text += "<stop>"
    text = text.replace("<prd>",".")
    text = re.sub('  +',' ',text)
    sents = text.split("<stop>")
    sents = sents[:-1]
    sents = [s.strip() for s in sents]
    return sents

def count_punctuation(t):
    punctuation = string.punctuation
    punctuation_count = len(filter(functools.partial(operator.contains, punctuation), t))
    textlength = len(t)
    relpc = 0
    if textlength>0:
        relpc = float(punctuation_count)/float(textlength)
    return relpc

def nrofsyllables(w):
    count = 0
    vowels = 'aeiouy'
    w = w.lower().strip(".:;?!")
    if w[0] in vowels:
        count +=1
    for index in range(1,len(w)):
        if w[index] in vowels and w[index-1] not in vowels:
            count +=1
    if w.endswith('e'):
        count -= 1
    if w.endswith('le'):
        count+=1
    if count == 0:
        count +=1
    return count

def fast_cosine_sim(a, b):
    if len(b) < len(a):
        a, b = b, a
    up = 0
    for key, a_value in a.iteritems():
        b_value = b.get(key, 0)
        up += a_value * b_value
    if up == 0:
        return 0
    return up / norm(a.values()) / norm(b.values())

def replace_quote(postcontent):
    adapted = ""
    blocks = re.split("\n\n",postcontent)
    #print blocks
    # first, find the block with the quote:
    bi=0
    bc = len(blocks)
    quoteblocki = 4
    while bi < bc:
        if " schreef op " in blocks[bi]:
            #print blocks[bi]
            quoteblocki = bi
            break

        # print until the quote:
        if not re.match('^>',blocks[bi]):
            adapted += blocks[bi]+"<br>\n"

        bi += 1
    blocks[quoteblocki] = re.sub("^>","",blocks[quoteblocki])
    blocks[quoteblocki] = re.sub("\(http://.*\):","",blocks[quoteblocki])
    #quote = blocks[quoteblocki]+blocks[quoteblocki+1]+"<br>\n"+blocks[quoteblocki+2]+"<br>\n"+blocks[quoteblocki+3]+"<br>\n"
    quote = blocks[quoteblocki]+"<br>\n"
    if len(blocks) > quoteblocki+1:
        quote += blocks[quoteblocki+1]+"<br>\n"

    #adapted += "<div style='background-color:rgb(240,240,240);padding-left:4em;padding-right:4em'>"+quote+"</div><br>\n"

    bi = quoteblocki+1
    while bi < bc:
        adapted += blocks[bi]+"<br>\n"
        bi += 1

    return adapted


columns = dict() # key is feature name, value is dict with key (threadid,postid) and value the feature value

def addvaluestocolumnsoverallthreads(dictionary,feature):
    global columns
    columndict = dict()
    if feature in columns: # if this is not the first thread, we already have a columndict for this feature
        columndict = columns[feature] # key is (threadid,postid) and value the feature value
    for (threadid,postid) in dictionary:
        value = dictionary[(threadid,postid)]
        columndict[(threadid,postid)] = value
    #print feature, columndict
    columns[feature] = columndict

def standardize_values(columndict,feature):
    values = list()
    for (threadid,postid) in columndict:
        values.append(columndict[(threadid,postid)])
    mean = numpy.mean(values)
    stdev = numpy.std(values)
    normdict = dict() # key is (threadid,postid) and value the normalized feature value
    for (threadid,postid) in columndict:
        value = columndict[(threadid,postid)]
        normvalue = 0.0
        if stdev == 0.0:
            stdev = 0.000000000001
            print "stdev is 0! ", feature, value, mean, stdev
        #if value != 0:
        normvalue = (float(value)-float(mean))/float(stdev)
        normdict[(threadid,postid)] = normvalue
#        if feature == "noofupvotes":
#           print threadid,postid, feature, float(value), mean, stdev, normvalue, len(columndict)

    return normdict


openingpost_for_thread = dict() # key is threadid, value is id of opening post
postids_dict = dict() # key is (threadid,postid), value is postid. Needed for pasting the columns at the end
threadids = dict() # key is (threadid,postid), value is threadid. Needed for pasting the columns at the end
threadids_list = list()
upvotecounts = dict()  # key is (threadid,postid), value is # of upvotes
responsecounts = dict()  # key is (threadid,postid), value is # of replies
cosinesimilaritiesthread = dict()  # key is (threadid,postid), value is cossim with term vector for complete thread
cosinesimilaritiestitle = dict()  # key is (threadid,postid), value is cossim with term vector for title
uniquewordcounts = dict()  # key is (threadid,postid), value is unique word count in post
wordcounts = dict() # key is (threadid,postid), value is word count in post
typetokenratios = dict()  # key is (threadid,postid), value is type-token ratio in post
abspositions = dict() # key is (threadid,postid), value is absolute position in thread
relpositions = dict()  # key is (threadid,postid), value is relative position in thread
relauthorcountsinthreadforpost = dict()  # key is (threadid,postid), value is relative number of posts by author in this thread
relpunctcounts = dict() # key is (threadid,postid), value is relative punctuation count in post
avgwordlengths = dict() # key is (threadid,postid), value is average word length (nr of characters)
avgnrsyllablesinwords = dict() # key is (threadid,postid), value is average word length (nr of syllables)
avgsentlengths = dict() # key is (threadid,postid), value is average word length (nr of words)
readabilities = dict() # key is (threadid,postid), value is readability
bodies = dict()  # key is (threadid,postid), value is content of post

#print time.clock(), "\t", "go through files"

for f in os.listdir(rootdir):
    if f.endswith("xml"):
        print time.clock(), "\t", f

        postids = list()
        termvectors = dict()  # key is postid, value is dict with term -> termcount for post
        termvectorforthread = dict()  # key is term, value is termcount for full thread
        termvectorfortitle = dict()  # key is term, value is termcount for title
        authorcountsinthread = dict()  # key is authorid, value is number of posts by author in this thread

        tree = ET.parse(rootdir+"/"+f)
        root = tree.getroot()

        for thread in root:
            threadid = thread.get('id')
            category = thread.find('category').text

            title = thread.find('title').text
            if title is None:
                # no title, then use complete opening post instead
                for posts in thread.findall('posts'):
                    title = posts.findall('post')[0].find('body').text

            if title is None:
                title = ""

            #print threadid,title

            titlewords = tokenize(title)
            for tw in titlewords:
                if tw in termvectorfortitle:
                    termvectorfortitle[tw] += 1
                else:
                    termvectorfortitle[tw] = 1
        # first go through the thread to find all authors
        for posts in thread.findall('posts'):
            for post in posts.findall('post'):
                author = post.find('author').text
                if author in authorcountsinthread:
                    authorcountsinthread[author] += 1
                else:
                    authorcountsinthread[author] =1

        for posts in thread.findall('posts'):
            noofposts = len(posts.findall('post'))
            if noofposts > 50:
                noofposts = 50
            postcount = 0

            #print time.clock(), "\t", "extract feats from each post"

            for post in posts.findall('post'):
                postcount += 1
                postid = post.get('id')

                if postcount == 1:
                    openingpost_for_thread[threadid] = postid
                    #print "opening post:",postid
                #print postid, postcount
                if 1 < postcount <= 51:
                    # don't include opening post in feature set
                    # and include at most 50 responses
                    postids.append(postid)
                    postids_dict[(threadid,postid)] = postid
                    threadids[(threadid,postid)] = threadid
                    threadids_list.append(threadid)
                    parentid = post.find('parentid').text

                    if parentid != openingpost_for_thread[threadid]:
                        # do not save responses for openingpost because openingpost will not be in feature file
                        # (and disturbs the column for standardization)
                        if (threadid,parentid) in responsecounts:
                            responsecounts[(threadid,parentid)] += 1
                        else:
                            responsecounts[(threadid,parentid)] = 1
                    #else:
                        #print "don't add responsecounts because opening post:", parentid

                    upvotes = 0
                    upvotesitem = post.find('upvotes')
                    if upvotesitem is None:
                        upvotes = 0
                    else :
                        upvotes = upvotesitem.text
                    if upvotes is None:
                        upvotes = 0
                    #print threadid,postid,upvotes, responsecounts[(threadid,parentid)]
                    upvotecounts[(threadid,postid)] = int(upvotes)


                    body = post.find('body').text
                    if postcount > 51:
                        continue
                    elif postid=="0":
                        continue
                    elif body is None:
                        body = ""
                    author = post.find('author').text
                    relauthorcountsinthreadforpost[(threadid,postid)] = float(authorcountsinthread[author])/float(noofposts)
                    #print threadid, postid, author, authorcountsinthread[author]

                    if " schreef op " in body:
                        body = replace_quote(body)
                        #print threadid, postid, body

                    if "smileys" in body:
                        body = re.sub(r'\((http://forum.viva.nl/global/(www/)?smileys/.*.gif)\)','',body)

                    if "http" in body:
                        body = re.sub(r'http://[^ ]+','',body)

                    bodies[(threadid,postid)] = body

                    words = tokenize(body)
                    wc = len(words)

                    sentences = split_into_sentences(body)
                    sentlengths = list()

                    for s in sentences:
                        sentwords = tokenize(s)
                        nrofwordsinsent = len(sentwords)
                        #print s, nrofwordsinsent
                        sentlengths.append(nrofwordsinsent)
                    if len(sentences) > 0:
                        avgsentlength = numpy.mean(sentlengths)
                        avgsentlengths[(threadid,postid)] = avgsentlength
                    else:
                        avgsentlengths[(threadid,postid)] = 0
                    relpunctcount = count_punctuation(body)
                    relpunctcounts[(threadid,postid)] = relpunctcount
                    #print body, punctcount
                    wordcounts[(threadid,postid)] = wc
                    uniquewords = dict()
                    wordlengths = list()
                    nrofsyllablesinwords = list()
                    for word in words:
                        #print word, nrofsyllables(word)
                        nrofsyllablesinwords.append(nrofsyllables(word))
                        wordlengths.append(len(word))
                        uniquewords[word] = 1
                        if word in termvectorforthread:  # dictionary over all posts
                           termvectorforthread[word] += 1
                        else:
                           termvectorforthread[word] = 1

                        worddict = dict()
                        if postid in termvectors:
                            worddict = termvectors[postid]
                        if word in worddict:
                            worddict[word] += 1
                        else:
                            worddict[word] = 1
                        termvectors[postid] = worddict

                    uniquewordcount = len(uniquewords.keys())
                    uniquewordcounts[(threadid,postid)] = uniquewordcount
                    readabilities[(threadid,postid)] = 0

                    if wc > 0:
                        avgwordlength = numpy.mean(wordlengths)
                        #avgnrsyllablesinword = numpy.mean(nrofsyllablesinwords)
                        avgwordlengths[(threadid,postid)] = avgwordlength
                        #avgnrsyllablesinwords[(threadid,postid)] = avgnrsyllablesinword
                        #readabilities[(threadid,postid)] = readability(avgnrsyllablesinword,avgsentlength)
                    else:
                        avgwordlengths[(threadid,postid)] = 0

                    #print threadid, postid, wc, avgnrsyllablesinword, avgsentlength, readability(avgnrsyllablesinword,avgsentlength)

                    typetokenratio = 0
                    if wordcounts[(threadid,postid)] > 0:
                        typetokenratio = float(uniquewordcount) / float(wordcounts[(threadid,postid)])
                    typetokenratios[(threadid,postid)] = typetokenratio

                    relposition = float(postcount)/float(noofposts)
                    #relposition = float(postid)/float(noofposts)
                    relpositions[(threadid,postid)] = relposition
                    abspositions[(threadid,postid)] = postcount

                    #abspositions[(threadid,postid)] = postid


        #print time.clock(), "\t", "fill term vectors"

        #print wordcounts
        # add zeroes for titleterms that are not in the thread vector
        for titleword in termvectorfortitle:
            if titleword not in termvectorforthread:
                termvectorforthread[titleword] = 0

        # add zeroes for terms that are not in the title vector:
        for word in termvectorforthread:
            if word not in termvectorfortitle:
                termvectorfortitle[word] = 0

        # add zeroes for terms that are not in the post vector:
        for postid in termvectors:
            worddictforpost = termvectors[postid]
            for word in termvectorforthread:
                if word not in worddictforpost:
                    worddictforpost[word] = 0
            termvectors[postid] = worddictforpost


        #    for term in termvectorforthread:
        #        print(postid,term,termvectors[postid][term])
            cossimthread = fast_cosine_sim(termvectors[postid], termvectorforthread)
            cossimtitle = fast_cosine_sim(termvectors[postid], termvectorfortitle)
            cosinesimilaritiesthread[(threadid,postid)] = cossimthread
            cosinesimilaritiestitle[(threadid,postid)] = cossimtitle

            #print postid, cossimthread



        #print time.clock(), "\t", "add missing feature values"


        for postid in postids:
            #print postid, abspositions[(threadid,postid)]
            if not (threadid,postid) in cosinesimilaritiesthread:
                cosinesimilaritiesthread[(threadid,postid)] = 0.0
            if not (threadid,postid) in cosinesimilaritiestitle:
                cosinesimilaritiestitle[(threadid,postid)] = 0.0
            if not (threadid,postid) in responsecounts:
                # don't store the counts for the openingpost
                #print "postid not in responsecounts", postid, "opening post:", openingpost_for_thread[threadid]
                responsecounts[(threadid,postid)] = 0


        #print time.clock(), "\t", "add feature values to columns for all threads"

        addvaluestocolumnsoverallthreads(threadids, "threadid")
        addvaluestocolumnsoverallthreads(postids_dict, "postid")

        addvaluestocolumnsoverallthreads(abspositions, "abspos")
        addvaluestocolumnsoverallthreads(relpositions, "relpos")
        addvaluestocolumnsoverallthreads(responsecounts, "noresponses")
        addvaluestocolumnsoverallthreads(upvotecounts, "noofupvotes")
        addvaluestocolumnsoverallthreads(cosinesimilaritiesthread, "cosinesimwthread")
        addvaluestocolumnsoverallthreads(cosinesimilaritiestitle, "cosinesimwtitle")
        addvaluestocolumnsoverallthreads(wordcounts, "wordcount")
        addvaluestocolumnsoverallthreads(uniquewordcounts, "uniquewordcount")
        addvaluestocolumnsoverallthreads(typetokenratios, "ttr")
        addvaluestocolumnsoverallthreads(relpunctcounts, "relpunctcount")
        addvaluestocolumnsoverallthreads(avgwordlengths, "avgwordlength")
        addvaluestocolumnsoverallthreads(avgsentlengths, "avgsentlength")
        addvaluestocolumnsoverallthreads(relauthorcountsinthreadforpost,"relauthorcountsinthread")



        #else:
        #    print "WARNING:", threadid, postid, "missing cosine sim", bodies[(threadid,postid)]
        #print threadid, postid, relpositions[(threadid,postid)], responsecounts[(threadid,postid)], wordcounts[(threadid,postid)], uniquewordcounts[(threadid,postid)], typetokenratios[(threadid,postid)]
        #print threadid, postid



columns_std = dict()

featnames = ("threadid","postid","abspos","relpos","noresponses","noofupvotes","cosinesimwthread","cosinesimwtitle","wordcount","uniquewordcount","ttr","relpunctcount","avgwordlength","avgsentlength","relauthorcountsinthread")

print time.clock(), "\t", "standardize feat values"


for featurename in featnames:
    columndict = columns[featurename]

    columndict_with_std_values = columndict
    if featurename != "postid" and featurename != "threadid":
        columndict_with_std_values = standardize_values(columndict,featurename)
    columns_std[featurename] = columndict_with_std_values


feat_weights = dict()
feat_weights["abspos"] = -0.69456
feat_weights["relpos"] = -0.17991
feat_weights["noresponses"] = -0.11507
feat_weights["noofupvotes"] = 0 # not in viva data
feat_weights["cosinesimwthread"] = 0.32817
feat_weights["cosinesimwtitle"] = 0.13588
feat_weights["wordcount"] = -1.44997
feat_weights["uniquewordcount"] = 1.90478
feat_weights["ttr"] = -0.38033
feat_weights["relpunctcount"] = -0.12664
feat_weights["avgwordlength"] = 0.18753
feat_weights["avgsentlength"] = 0 # not significant
feat_weights["relauthorcountsinthread"] =  -0.11927

intercept = 2.45595

#(Intercept)              2.45595    0.03381  72.646  < 2e-16 ***
#abspos                  -0.69456    0.07358  -9.440  < 2e-16 ***
#relpos                  -0.17991    0.07159  -2.513 0.012025 *
#noresponses             -0.11507    0.03386  -3.399 0.000686 ***
#cosinesimwthread         0.32817    0.07379   4.447 9.02e-06 ***
#cosinesimwtitle          0.13588    0.03523   3.857 0.000117 ***
#wordcount               -1.44997    0.17763  -8.163 4.81e-16 ***
#uniquewordcount          1.90478    0.19878   9.582  < 2e-16 ***
#ttr                     -0.38033    0.06543  -5.813 6.81e-09 ***
#relpunctcount           -0.12664    0.03995  -3.170 0.001541 **
#avgwordlength            0.18753    0.04156   4.512 6.67e-06 ***
#avgsentlength           -0.01406    0.04058  -0.347 0.728958
#relauthorcountsinthread -0.11927    0.03410  -3.498 0.000476 ***

selected_posts = dict() # key is thread id, value is dict with postid -> predicted # of votes (predicted_outcome by LRM)

columnnames = list(featnames)
columnnames.append("predicted")
columnnames.append("selected_based_on_threshold")

out = open(outfilename,'w')

for columnname in columnnames:
    out.write(columnname+"\t")
out.write("\n")


for (threadid,postid) in threadids:
    predicted_outcome = intercept
    #out.write(threadid+"\t"+postid+"\t")
    for featurename in featnames:
        columndict_with_std_values = columns_std[featurename]
        value = columndict_with_std_values[(threadid,postid)]
        out.write(str(value)+"\t")
        if featurename in feat_weights:
            weighted_value = feat_weights[featurename]*value
            #print value, weighted_value
            predicted_outcome += weighted_value
    out.write(str(predicted_outcome)+"\t")
    if predicted_outcome >= 3.72:
        # fixed threshold, based on tune set 5 from viva data
        out.write("1")
    else:
        out.write("0")
    out.write("\n")
        #print threadid,postid,linear_combination
#        selected_posts_for_thread = dict()
#        if threadid in selected_posts:
#            selected_posts_for_thread = selected_posts[threadid]
#        selected_posts_for_thread[postid] = predicted_outcome
#        selected_posts[threadid] = selected_posts_for_thread


out.close()


