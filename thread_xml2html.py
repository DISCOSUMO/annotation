# thread_xml2html.py 2ny4u1.xml

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


xmlfile = sys.argv[1]
htmlfile = xmlfile.replace("xml","html")
out = open(htmlfile,'w')

with open("header.html",'r') as header:
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
print forumtype
if forumtype == "viva":
    hierarchy = False
if forumtype == "reddit":
    hierarchy = True
#print forumtype, hierarchy

instructions = '<td width="50%" style="padding-left:2em;padding-right:1em"><h2>Complete forum thread</h2></td>' \
               '<td width="50%" style="padding-left:2em;padding-right:1em"><h2>Your selection</h2></td></tr>\n<tr>' \
               '<td style="padding-left:2em;padding-right:1em">Please select the posts ' \
               '(by clicking on them one by one) that you think are the most important ' \
               'for the thread. You can determine the number of selected posts yourself.' \
               '<br><br></td><td style="padding-left:2em;padding-right:1em">' \
               'You can remove posts from your selection by clicking on them.<br>' \
               'Click the \"Submit selection of posts\"-button when your selection is complete.<br><br>' \
               '</td>'

if forumtype == "viva":
    instructions = '<td width="50%" style="padding-left:2em;padding-right:1em"><h2>Volledige topic</h2></td>' \
               '<td width="50%" style="padding-left:2em;padding-right:1em"><h2>Jouw selectie</h2></td></tr>\n<tr>' \
               '<td style="padding-left:2em;padding-right:1em">Selecteer de posts ' \
               '(door ze &eacute;&eacute;n voor &eacute;&eacute;n aan te klikken) die volgens jou het belangrijkst zijn ' \
               'voor voor het topic. Je bepaalt zelf hoeveel posts je selecteert.' \
                '<br><br></td><td style="padding-left:2em;padding-right:1em">' \
                'Als je hieronder de door jou geselecteerde posts leest, kun je checken of je een goede samenvatting van het topic hebt gemaakt. ' \
               'Je kunt een post weer verwijderen uit je selectie door erop te klikken.<br>' \
               'Klik op de \"Verzend selectie\"-knop als je selectie af is. Als je geen enkele post' \
               ' hebt geselecteerd voor dit topic, leg dan in het opmerkingen-veld uit waarom.<br><br>' \
               '</td>'

out.write('<table width="100%">\n<tr>'+instructions+'</tr> </table>\n')




out.write('<form name="selectedposts" action="../../../../cgi-bin/show_thread.pl" method="post">\n')
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
            postcount += 1
            if postcount > 50:
                break
            list_of_posts.append(post)
            postid = post.get('id')
            postids[postid] = post
            parentid = post.find('parentid').text
            if parentid is not None:
                children_of_parent = list()
                if children.has_key(parentid):
                    children_of_parent = children[parentid]
                children_of_parent.append(postid)
                #print "parent:",parentid,"child:",postid
                children[parentid] = children_of_parent

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

row=0

postidperrow = dict()
openingpostwithauthor = ""
def print_post(currentpostid,indent):
    global row
    global openingpostwithauthor
    currentpost = postids[currentpostid]
    author = currentpost.find('author').text
    timestamp = currentpost.find('timestamp').text
    bodyofpost = currentpost.find('body').text

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

    if currentpostid == "0":
        openingpostwithauthor = bodywithauthor
        #print openingpostwithauthor
    bodywithauthorforclick = re.sub("\'","\\\'",bodywithauthor)
    out.write("<tr>")
    row += 1
    out.write('<td>')
    if row==1:
        bgcolor="rgb(240,240,240)"
    else:
        bgcolor="white"
    out.write('<a href="#" class="list-group-item" style="background-color:'+bgcolor+'; padding-left:'+str(indent)+'em" ')
    out.write('onclick="addTxt(\''+currentpostid+'\',\'selected\');')
    out.write('getElementById(\'row'+str(row)+'\').innerHTML=\''+bodywithauthorforclick+'\';return false;">')
    out.write(bodywithauthor)
    out.write('\n')
    postidperrow[row] = currentpostid
    if upvotefield is not None and downvotefield is not None:

        upvotes = currentpost.find('upvotes').text
        downvotes = currentpost.find('downvotes').text
        score = int(upvotes)-int(downvotes)
        out.write('<div style="font-size:8pt;border-style:none">'+str(score)+' points on reddit</div>\n')

    out.write("</a></td></tr>\n")



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

#print_children(id_of_firstpost,"")

title=""
noofposts = 0
threadid = ""
for thread in root:
    threadid = thread.get('id')
    category = thread.find('category').text
    title = thread.find('title').text
    out.write('<a href="#" class="list-group-item active" style="padding-left:2em">[category: '+category+']<br><br>\n<b>'+title+'</b></a>\n')
    out.write('<table border=1 width="100%">\n')
    #for posts in thread.findall('posts'):
        #id_of_firstpost = firstpost.get('id')
    id_of_firstpost = list_of_posts[0].get('id')
    noofposts = len(list_of_posts)
    if hierarchy:
        print_children(id_of_firstpost,0)
    else:
        for post in list_of_posts:
            postid = post.get('id')
            print_post(postid,2)

    out.write("</table>\n")

out.write('</div>\n</div>\n')

out.write('<div class="col-sm-6">\n')
out.write('<div class="list-group">\n')
out.write('<a href="#" class="list-group-item active" style="padding-left:2em">[category: '+category+']<br><br>\n<b>'+title+'</b></a>\n')
out.write('<table border=1 width="100%">\n')
out.write("<tr>")
out.write('<td width="100%">')
out.write('<a href="#" class="list-group-item" style="padding-left:2em"  id="row'+str(1)+'" onclick="'
    'addTxt(\'-'+postidperrow[1]+'\',\'selected\');')
out.write('getElementById(\'row'+str(1)+'\').innerHTML=\'...\'">'+openingpostwithauthor)
#out.write('<td width="100%"  style="padding-left:2em;padding-right:1em"><a href="#" >...</a></td>')
out.write("</a></td>\n")
out.write("</tr>\n")
for i in range (2,noofposts+1):
    out.write("<tr>")
    out.write('<td width="100%">')
    out.write('<a href="#" class="list-group-item" style="padding-left:2em"  id="row'+str(i)+'" onclick="'
        'addTxt(\'-'+postidperrow[i]+'\',\'selected\');')
    out.write('getElementById(\'row'+str(i)+'\').innerHTML=\''+'...'+'\'">...')
    #out.write('<td width="100%"  style="padding-left:2em;padding-right:1em"><a href="#" >...</a></td>')
    out.write("</a></td>\n")
    out.write("</tr>\n")
out.write("</table>\n")
out.write('</div>\n</div>\n')

#Also ask them to indicate:
#   their familiarity with the topic of the thread (scale 1-5)
#   their familiarity with reddit (scale 1-5)
#   how useful a summary of the thread would be for a reddit visitor on a mobile device (scale 1-5)
#   and give room for additional comments

out.write('Geef op een schaal van 1 tot 5 aan hoe vertrouwd je bent met het onderwerp'
          ' dat wordt besproken in dit topic:<br>\n'
          '<input type="radio" name="familiarity" value="1">&nbsp;&nbsp;&nbsp;1 (totaal niet vertrouwd)<br>\n'
          '<input type="radio" name="familiarity" value="2">&nbsp;&nbsp;&nbsp;2<br>'
          '<input type="radio" name="familiarity" value="3">&nbsp;&nbsp;&nbsp;3<br>'
          '<input type="radio" name="familiarity" value="4">&nbsp;&nbsp;&nbsp;4<br>'
          '<input type="radio" name="familiarity" value="5">&nbsp;&nbsp;&nbsp;5 (heel vertrouwd)<br>')
out.write('<br>Geef op een schaal van 1 tot 5 aan hoe nuttig je het zou vinden om voor dit topic de mogelijkheid te hebben '
          'om alleen de belangrijkste posts te zien (bijvoorbeeld op een mobiel of tablet):<br>\n'
          '<input type="radio" name="utility" value="1a">&nbsp;&nbsp;&nbsp;1 (totaal niet nuttig want <b>alles</b> is even belangrijk)<br>\n'
          '<input type="radio" name="utility" value="1n">&nbsp;&nbsp;&nbsp;1 (totaal niet nuttig want <b>niets</b> is belangrijk)<br>\n'
          '<input type="radio" name="utility" value="1o">&nbsp;&nbsp;&nbsp;1 (totaal niet nuttig om een andere reden)<br>\n'
          '<input type="radio" name="utility" value="2">&nbsp;&nbsp;&nbsp;2<br>'
          '<input type="radio" name="utility" value="3">&nbsp;&nbsp;&nbsp;3<br>'
          '<input type="radio" name="utility" value="4">&nbsp;&nbsp;&nbsp;4<br>'
          '<input type="radio" name="utility" value="5">&nbsp;&nbsp;&nbsp;5 (heel nuttig)<br>')
out.write('<br>Opmerkingen (verplicht als je geen enkele post hebt geselecteerd):'
          '<br><input type="text" size="80" name="comments"><br><br>\n')
out.write('<input type="hidden" name="threadid" value="'+threadid+'">\n')
out.write('<input type="hidden" name="forumtype" value="'+forumtype+'">\n')
out.write('<input type="hidden" id="selected" name="selected" size="40">\n')

submittext = "Submit selection of posts and go to next thread"
if forumtype == "viva":
    submittext = "Verzend selectie en ga naar het volgende topic"
out.write('<input type="submit" value="'+submittext+'">\n')
out.write('</form>\n')

with open("footer.html",'r') as header:
    for line in header:
        out.write(line)

sys.stderr.write("Output written to "+out.name+"\n")

out.close()