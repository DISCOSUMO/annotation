# thread_summary_xml2html.py ../dataconversion/Viva_forum/samples/kankerthreads/ kankerthreads.postfeats.norm+selected.out kankerthreads_summaries_list.html
# thread_summary_xml2html.py ../dataconversion/GIST_FB/threads gistfb.postfeats.norm+selected.out gistfb_summaries_list.html

import os
import sys
reload(sys)
sys.setdefaultencoding('utf8')
import re
import math
import fileinput
from collections import defaultdict
import xml.etree.ElementTree as ET

hierarchy = False

rootdir = sys.argv[1]
selectedfile = sys.argv[2]
outfile = sys.argv[3]
postselected = dict()

indexhtml = open(outfile,'w')


with open(selectedfile,'r') as featfile:
    for line in featfile:
        #threadid	postid	abspos	relpos	noresponses	cosinesimwthread	cosinesimwtitle	wordcount	uniquewordcount	ttr	relpunctcount	avgwordlength	avgsentlength	relauthorcountsinthread	predicted	selected_based_on_threshold
        columns = line.split("\t")
        threadid = columns[0]
        postid = columns[1]
        selected = columns[-1].rstrip()
        postselected[(threadid,postid)] = selected
        #print threadid,postid,selected


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


def print_children(leaf,indent): # leaf is a post id, indent is the size of the indentation, row is the nth row of the list
    global row
    indent += 3
    #print indent,leaf
    currentpostid = leaf
    print_post(currentpostid,indent)

    if children.has_key(leaf):
        children_of_leaf = children[leaf]
        #print "has children", children_of_leaf
        for child in children_of_leaf:
            print_children(child,indent)


row=0

postidperrow = dict()
openingpostwithauthor = ""
def print_post(currentpostid,indent):
    global row
    global openingpostwithauthor

    if currentpostid == "0" or (threadid,currentpostid) in postselected:
        # don't print posts that somehow did not get classified and therefore missing in gistfb.postfeats+selected.out

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
            indexhtml.write('<li><a href="threads/'+threadid+'.html" target="_blank"><b>'+author+'</b> @ '+timestamp+'</a>: '+bodyofpost+'</li>\n')
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
        #print threadid, currentpostid
        if currentpostid == "0":
            out.write(bodywithauthor)
        elif (threadid,currentpostid) in postselected:
            #out.write(postselected[(threadid,currentpostid)])
            #print threadid, currentpostid, postselected[(threadid,currentpostid)]
            if postselected[(threadid,currentpostid)] == "1":
                out.write(bodywithauthor)
                #print bodywithauthor
            else:
                out.write('<b>'+author+'</b> @ '+timestamp+':<br> ''<button type="button" class="btn btn-primary" data-toggle="collapse" data-target="#coll'+currentpostid+'">Klap reactie uit</button><div id="coll'+currentpostid+'" class="collapse">'+bodyofpost+'</div>')
        out.write('\n')
        postidperrow[row] = currentpostid
        if upvotefield is not None and downvotefield is not None:

            upvotes = currentpost.find('upvotes').text
            downvotes = currentpost.find('downvotes').text
            score = int(upvotes)-int(downvotes)
            out.write('<div style="font-size:8pt;border-style:none">'+str(score)+' likes</div>\n')

        out.write("</a></td></tr>\n")




for f in os.listdir(rootdir):
    if f.endswith("xml"):
        #print f
        xmlfile = rootdir+"/"+f
        htmlfile = xmlfile.replace("xml","html")
        out = open(htmlfile,'w')


        with open("header4summary.html",'r') as header:
            for line in header:
                if re.match(".*<title>.*",line):
                    out.write("<title>"+xmlfile+"</title>")
                else:
                    out.write(line)



        children = dict() # key is parentid, value is list of children ids
        postids = dict() # key is postid, value is post

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

        out.write('<div class="col-sm-8">\n')
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
                    postid = post.get('id')
                    #postid = postcount
                    if postcount == 0:
                        postid = "0"
                    postids[str(postid)] = post
                    parentid = post.find('parentid').text
                    if parentid is not None:
                        children_of_parent = list()
                        if children.has_key(parentid):
                            children_of_parent = children[parentid]
                        children_of_parent.append(postid)
                        #print "parent:",parentid,"child:",postid
                        children[parentid] = children_of_parent
                    postcount += 1




        #print_children(id_of_firstpost,"")
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
            #id_of_firstpost = list_of_posts[0].get('id')
            id_of_firstpost = "0"
            noofposts = len(list_of_posts)
            if hierarchy:
                print_children(id_of_firstpost,0)
            else:
                postcount = 0
                for post in list_of_posts:
                    postid = post.get('id')
                    indent = 4
                    if postcount== 0:
                        postid = "0"
                        indent = 2
                    print_post(str(postid),indent)
                    postcount += 1
                    #postid = post.get('id')


            out.write("</table>\n")

        out.write('</div>\n</div>\n')



        #Also ask them to indicate:
        #   their familiarity with the topic of the thread (scale 1-5)
        #   their familiarity with reddit (scale 1-5)
        #   how useful a summary of the thread would be for a reddit visitor on a mobile device (scale 1-5)
        #   and give room for additional comments


        with open("footer.html",'r') as header:
            for line in header:
                out.write(line)

        sys.stderr.write("Output written to "+out.name+"\n")

        out.close()

indexhtml.close()