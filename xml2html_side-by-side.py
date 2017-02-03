# coding=utf-8
#  xml2html_side-by-side.py sample_viva/

import os
import sys
import re
from random import randint
import xml.etree.ElementTree as ET

hierarchy = False

rootdir = sys.argv[1]

postselected = dict()
postvotes_A = dict()
postvotes_B = dict()
postvotes_C = dict()
postvotes_D = dict()
postvotes = dict() # key is [ABC], value is postvotes_A, postvotes_B, postvotes_C or postvotes_D
postvotes["A"] = postvotes_A
postvotes["B"] = postvotes_B
postvotes["C"] = postvotes_C
postvotes["D"] = postvotes_D

usernames = dict()
usernames["F."] = "A"
usernames["Judith"] = "B"
usernames["Niree Bakker"] = "C"
usernames["Lian Bouten"] = "D"

with open("evaluation/postfeats+selectedGeneric.out",'r') as featfile:
    for line in featfile:
        #threadid	abspos	relpos	noresponses	cosinesimwthread	cosinesimwtitle	wordcount	uniquewordcount	ttr	relpunctcount	avgwordlength	avgsentlength	relauthorcountsinthread	nrofvotes	predicted	selected based on threshold
        columns = line.split("\t")
        threadid = columns[0]
        postid = columns[1]
        selected = columns[15].rstrip()
        postselected[(threadid,postid)] = selected
        #print "Generic",threadid,postid,selected

with open("evaluation/postfeats.F..out",'r') as featfile:
    for line in featfile:
        #threadid	abspos	relpos	noresponses	cosinesimwthread	cosinesimwtitle	wordcount	uniquewordcount	ttr	relpunctcount	avgwordlength	avgsentlength	relauthorcountsinthread	nrofvotes
        columns = line.split("\t")
        threadid = columns[0]
        postid = columns[1]
        selected = columns[13].rstrip()
        postvotes_A[(threadid,postid)] = selected
        #print ("A",threadid,postid,selected)

with open("evaluation/postfeats.Judith.out",'r') as featfile:
    for line in featfile:
        #threadid	abspos	relpos	noresponses	cosinesimwthread	cosinesimwtitle	wordcount	uniquewordcount	ttr	relpunctcount	avgwordlength	avgsentlength	relauthorcountsinthread	nrofvotes
        columns = line.split("\t")
        threadid = columns[0]
        postid = columns[1]
        selected = columns[13].rstrip()
        postvotes_B[(threadid,postid)] = selected
        #print ("B",threadid,postid,selected)

with open("evaluation/postfeats.Niree_Bakker.out",'r') as featfile:
    for line in featfile:
        #threadid	abspos	relpos	noresponses	cosinesimwthread	cosinesimwtitle	wordcount	uniquewordcount	ttr	relpunctcount	avgwordlength	avgsentlength	relauthorcountsinthread	nrofvotes
        columns = line.split("\t")
        threadid = columns[0]
        postid = columns[1]
        selected = columns[13].rstrip()
        postvotes_C[(threadid,postid)] = selected
        print ("C",threadid,postid,selected)

with open("evaluation/postfeats.Lian_Bouten.out",'r') as featfile:
    for line in featfile:
        #threadid	abspos	relpos	noresponses	cosinesimwthread	cosinesimwtitle	wordcount	uniquewordcount	ttr	relpunctcount	avgwordlength	avgsentlength	relauthorcountsinthread	nrofvotes
        columns = line.split("\t")
        threadid = columns[0]
        postid = columns[1]
        selected = columns[13].rstrip()
        postvotes_D[(threadid,postid)] = selected
        #print ("D",threadid,postid,selected)

#sys.exit()

crossuser = dict()
threadsforA = list()
threadsforB = list()
threadsforC = list()
threadsforD = list()
threadsfor = dict() # key is [ABCD], value is threadsfor_A, threadsfor_B, threadsfor_C or threadsfor_D
threadsfor["A"] = threadsforA
threadsfor["B"] = threadsforB
threadsfor["C"] = threadsforC
threadsfor["D"] = threadsforD

with open("cross-user-sample.txt",'r') as crossusersample:
    for line in crossusersample:
        #threadid	other_for_F	other_for_Judith	other_for_Niree Bakker
        line = line.rstrip()
        columns = line.split("\t")
        threadid = columns[0]
        if re.match("[0-9]",threadid):
            forA = columns[1]
            forB = columns[2]
            forC = columns[3]
            forD = columns[4]
            if forA is not "x":
                crossuser[(threadid,"A")] = usernames[forA]
                threadsforA.append(threadid)
            if forB is not "x":
                crossuser[(threadid,"B")] = usernames[forB]
                threadsforB.append(threadid)
            if forC is not "x":
                crossuser[(threadid,"C")] = usernames[forC]
                threadsforC.append(threadid)
            if forD is not "x":
                crossuser[(threadid,"D")] = usernames[forD]
                threadsforD.append(threadid)



#for (threadid,rater) in crossuser:
#    print (threadid, rater, crossuser[(threadid,rater)])

sys.stderr.write("Read files in "+rootdir+"\n")

def replace_quote(postcontent):
    adapted = ""
    #&gt; quote:

    #&gt;

    #&gt; **[fireandice schreef op 16 juni 2014 @
    #22:20](http://forum.viva.nl/forum/list_message/16388654#m16388654):**

    #waarom wil je ze niet met deze man, zijn die voorvallen zo erg dat je hem
    #nooit meer wilt zien of kun je hem nog wel als vriend zien?
    postcontent = re.sub("\n"," ",postcontent)
    #print postcontent
    blocks = re.split("<br>",postcontent)
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

    #if len(blocks) > quoteblocki+3:
    #    quote += blocks[quoteblocki+3]
    #if len(blocks) > quoteblocki+4:
    #    quote += blocks[quoteblocki+4]
        #print bc, blocks[quoteblocki], blocks[quoteblocki+1], blocks[quoteblocki+2], blocks[quoteblocki+3], blocks[quoteblocki+4]
    adapted += "<div style='background-color:rgb(240,240,240);padding-left:4em;padding-right:4em'>"+quote+"</div><br>\n"

    bi = quoteblocki+2
    while bi < bc:
        adapted += blocks[bi]+"<br>\n"
        bi += 1


    return adapted


def print_children(leaf,indent,postvotes,which): # leaf is a post id, indent is the size of the indentation, row is the nth row of the list
    global row
    indent += 3
    #print indent,leaf
    currentpostid = leaf
    print_post(currentpostid,indent,postvotes,which)

    if leaf in children:
        children_of_leaf = children[leaf]
        #print "has children", children_of_leaf
        for child in children_of_leaf:
            print_children(child,indent,postvotes,which)


row=0

postidperrow = dict()
openingpostwithauthor = ""
def print_post(currentpostid,indent,postvotes,which):
    global row
    global openingpostwithauthor
    #print currentpostid
    if currentpostid == "0" or (threadid,currentpostid) in postvotes:
        # don't print posts that somehow did not get classified and therefore missing in postfeats+selected.out

        currentpost = postids[currentpostid]
        author = currentpost.find('author').text
        timestamp = currentpost.find('timestamp').text
        bodyofpost = currentpost.find('body').text

        #print author, timestamp

        if bodyofpost is None:
            bodyofpost = ""
        if re.match(".*http://[^ ]+\n[^ ]+.*",bodyofpost):
            #print bodyofpost
            bodyofpost = re.sub("(http://[^ ]+)\n([^ ]+)",r"\1\2",bodyofpost)
            #print bodyofpost

        bodyofpost = re.sub("\"","&#34;",bodyofpost)
        #bodyofpost = re.sub("\'","&#39;",bodyofpost)
        #bodyofpost = re.sub("\'","\\\'",bodyofpost)
        bodyofpost = re.sub("\n *\n","<br>\n",bodyofpost)
        #print currentpostid, bodyofpost
        if " schreef op " in bodyofpost:
            #print currentpostid
            bodyofpost = replace_quote(bodyofpost)

        bodyofpost = re.sub("\n"," ",bodyofpost)

        if "smileys" in bodyofpost:
            bodyofpost = re.sub(r'\((http://forum.viva.nl/global/(www/)?smileys/.*.gif)\)','',bodyofpost)
            #print bodyofpost

        #if "http" in bodyofpost:
            #print currentpostid
        #    urlpattern = re.compile(r"(http:[^ )]+)")
        #    bodyofpost = urlpattern.sub(r'<a href=\"\1\" target=\"_blank\">\1</a>',bodyofpost)

        upvotefield = currentpost.find('upvotes')
        downvotefield = currentpost.find('downvotes')

        bodywithauthor = '<b>'+author+'</b> @ '+timestamp+':<br> '+bodyofpost
        #print currentpostid, bodywithauthor

        if currentpostid == "0":
            openingpostwithauthor = bodywithauthor
            #print openingpostwithauthor
        out.write("<tr>")
        row += 1
        out.write('<td>')
        if row==1:
            bgcolor="rgb(240,240,240)"
        else:
            bgcolor="white"
        out.write('<a href="#/" class="list-group-item" style="background-color:'+bgcolor+'; padding-left:'+str(indent)+'em" ')
        out.write('>')
        if currentpostid == "0":
            out.write(bodywithauthor)
        elif (threadid,currentpostid) in postselected:
            #out.write(postselected[(threadid,currentpostid)])

            if postvotes[(threadid,currentpostid)] == "1":
                out.write(bodywithauthor)
            else:
                out.write('<b>'+author+'</b> @ '+timestamp+':<br> ''<button type="button" class="btn btn-primary" data-toggle="collapse" data-target="#coll'+which+"_"+currentpostid+'">Klap verborgen reactie uit</button><div id="coll'+which+"_"+currentpostid+'" class="collapse">'+bodyofpost+'</div>')
        out.write('\n')
        postidperrow[row] = currentpostid
        if upvotefield is not None and downvotefield is not None:

            upvotes = currentpost.find('upvotes').text
            downvotes = currentpost.find('downvotes').text
            score = int(upvotes)-int(downvotes)
            out.write('<div style="font-size:8pt;border-style:none">'+str(score)+' likes</div>\n')

        out.write("</a></td></tr>\n")

    #else:
      #  print "not in postvotes:",threadid, currentpostid, which


children = dict() # key is parentid, value is list of children ids
postids = dict() # key is postid, value is post
def print_summary(out,root,postvotes,which):
    global children
    global postids

    out.write('<div class="col-sm-6">\n')
    out.write('<div class="list-group">\n')

    list_of_posts = list()
    maxnrofposts = 50
    for thread in root:

        for posts in thread.findall('posts'):
            firstpost = posts.findall('post')[0]
            #id_of_firstpost = firstpost.get('id')
            postcount = 0
            for post in posts.findall('post'):

                if postcount > 50:
                    break
                list_of_posts.append(post)
                #postid = post.get('id')
                postid = postcount
                #if not (thread.get('id'),postid) in postvotes:
                 #   print "not in postvotes:", thread.get('id'), postid
                postids[str(postid)] = post
                parentid = post.find('parentid').text
                if parentid is not None:
                    children_of_parent = list()
                    if parentid in children:
                        children_of_parent = children[parentid]
                    children_of_parent.append(postid)
                    #print "parent:",parentid,"child:",postid
                    children[parentid] = children_of_parent
                postcount += 1


    #print_children(id_of_firstpost,"",postvotes,which)

    title=""
    noofposts = 0
    threadid = ""
    for thread in root:
        threadid = thread.get('id')
        #print threadid
        category = thread.find('category').text
        if category is None:
            category = ""
        title = thread.find('title').text
        if title is None:
            title = ""
        out.write('<a href="#" class="list-group-item active" style="padding-left:2em">[category: '+category+']<br><br>\n<b>'+title+'</b></a>\n')
        out.write('<table border=1 width="100%">\n')
        #for posts in thread.findall('posts'):
            #id_of_firstpost = firstpost.get('id')
        id_of_firstpost = list_of_posts[0].get('id')
        noofposts = len(list_of_posts)
        if hierarchy:
            print_children(id_of_firstpost,0,postvotes,which)
        else:
            postcount = 0
            for post in list_of_posts:
                postid = postcount
                #print postid
                print_post(str(postid),2,postvotes, which)
                postcount += 1
                #postid = post.get('id')


        out.write("</table>\n")

    out.write('</div>\n</div>\n')


for self in ("A","B","C","D"):

    fordir = "for"+self
    for fi in os.listdir("evaluation/"+fordir):
        os.remove("evaluation/"+fordir+"/"+fi)

    for f in os.listdir(rootdir):
        if f.endswith("xml"):

            threadid = f.replace(".xml","")

            if threadid in threadsfor[self]:
                other = crossuser[(threadid,self)]
                postvotes_other = postvotes[other]
                postvotes_self = postvotes[self]
                postvotes_model = postselected
                #print postvotes_model
                summaries = dict()
                summaries[1] = postvotes_other
                summaries[2] = postvotes_self
                summaries[3] = postvotes_model

                for v1 in (1,2,3):
                    for v2 in (1,2,3):
                        if v2 > v1:

                            postvotes1 = summaries[v1]
                            postvotes2 = summaries[v2]
                            xmlfile = rootdir+"/"+f
                            htmlfile = xmlfile.replace("xml",str(v1)+"-vs-"+str(v2)+".html")

                            if randint(0,1) == 1:
                                postvotes1 = summaries[v2]
                                postvotes2 = summaries[v1]
                                htmlfile = xmlfile.replace("xml",str(v2)+"-vs-"+str(v1)+".html")


                            htmlfile = htmlfile.replace(rootdir,"evaluation/"+fordir)
                            out = open(htmlfile,'w')


                            with open("header4summary.html",'r') as header:
                                for line in header:
                                    if re.match(".*<title>.*",line):
                                        out.write("<title>"+xmlfile+"</title>")
                                    else:
                                        out.write(line)

                            out.write('<form name="selectedposts" action="../../../../cgi-bin/show_summaries.pl" method="post">\n')

                            out.write('<table width="100%">\n')
                            out.write('<tr><td colspan="2" align="center">')
                            out.write('Geef aan welke samenvatting van het topic je beter vindt<br>\n'
                                      '<input type="radio" name="compare" value="A++">&nbsp;&nbsp;&nbsp;A is veel beter'
                                      '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<input type="radio" name="compare" value="A+">&nbsp;&nbsp;&nbsp;A is een beetje beter'
                                      '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<input type="radio" name="compare" value="0">&nbsp;&nbsp;&nbsp;A en B zijn even goed'
                                      '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<input type="radio" name="compare" value="B+">&nbsp;&nbsp;&nbsp;B is een beetje beter'
                                      '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<input type="radio" name="compare" value="B++">&nbsp;&nbsp;&nbsp;B is veel beter'
                                      '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<input type="radio" name="compare" value="NA">&nbsp;&nbsp;&nbsp;Ik weet het niet')
                            out.write('<br><br>Opmerkingen (verplicht als je "Ik weet het niet" hebt geselecteerd):'
                                      '<br><input type="text" size="80" name="comments"><br><br>\n')
                            out.write('<input type="hidden" name="threadid" value="'+threadid+'">\n')
                            out.write('<input type="hidden" name="versus" value="'+htmlfile+'">\n')

                            out.write('</td></tr>')
                            out.write('<tr><td colspan="2" align="center"><input type="submit" value="Verstuur"></td></tr>'
                                      '<tr>'+'<td width="50%" style="padding-left:2em;padding-right:1em"><h2>Samenvatting A</h2></td>' \
                                   '<td width="50%" style="padding-left:2em;padding-right:1em"><h2>Samenvatting B</h2></td></tr>\n<tr>' \
                                   '</td>'+'</tr> </table>\n')
                            out.write('</form>\n')


                            tree = ET.parse(xmlfile)
                            root = tree.getroot()
                            id_of_firstpost = ""
                            forumtype = root.get('type')
                            #print forumtype
                            if forumtype == "viva":
                                hierarchy = False
                            if forumtype == "reddit":
                                hierarchy = True
                            #print forumtype, hierarchy

                            print_summary(out,root,postvotes1,"1")
                            print_summary(out,root,postvotes2,"2")


                            with open("footer.html",'r') as header:
                                for line in header:
                                    out.write(line)

                            sys.stderr.write("Output written to "+out.name+"\n")

                            out.close()

