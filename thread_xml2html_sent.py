# coding=utf-8
# thread_xml2html_sent.py 160543202978_10153102470587979.xml
# thread_xml2html_sent.py ../dataconversion/NL_GIST_forum/samples/50long10threads/948.xml

import os
import sys
import re
import xml.etree.ElementTree as ET
import numpy

hierarchy = False


xmlfile = sys.argv[1]
htmlfile = xmlfile.replace("xml","html")
htmlsentfile = htmlfile.replace(".html",".sent.html")
out = open(htmlfile,'w')
outsent = open(htmlsentfile,'w')


with open("header.html",'r') as header:
    for line in header:
        if re.match(".*<title>.*",line):
            out.write("<title>"+xmlfile+"</title>")
            outsent.write("<title>"+xmlfile+"</title>")
        else:
            out.write(line)
            outsent.write(line)



children = dict() # key is parentid, value is list of children ids
postids = dict() # key is postid, value is post

tree = ET.parse(xmlfile)
root = tree.getroot()
id_of_firstpost = ""
forumtype = root.get('type')
print (forumtype)
if forumtype == "viva" or forumtype == "fb" or forumtype == "bb":
    hierarchy = False
if forumtype == "reddit":
    hierarchy = True
#print forumtype, hierarchy

instructions = '<td width="50%" style="padding-left:2em;padding-right:1em"><h2>Complete forum thread</h2></td>' \
               '<td width="50%" style="padding-left:2em;padding-right:1em"><h2>Your summary</h2></td></tr>' \
               '<td style="padding-left:2em;padding-right:1em">Please select the pieces of text ' \
               'that you think are the most important ' \
               'for the thread. You can either select a post as a whole (by clicking "select the complete post") ' \
               'or select separate sentence(s) from a post. ' \
               'You can determine the number of selected posts yourself but try to be concise so that the resulting summary does not contain too much redundant information. ' \
               'The selected text together should' \
               ' form an informative summary of the thread.' \
               '<br><br></td><td style="padding-left:2em;padding-right:1em">' \
               'Each [...] is a placeholder for a sentence from the original thread. You can remove posts from your selection by clicking on them. You can not remove separate sentences. ' \
               'If you want to remove a sentence, remove the post and then re-select the correct sentences.<br><br><br><br><br>' \
               '</td>'

if forumtype == "viva":
    instructions = '<td width="33%" style="padding-left:2em;padding-right:1em"><h2>Volledige topic</h2></td>' \
               '<td width="33%" style="padding-left:2em;padding-right:1em"><h2>Jouw selectie</h2></td></tr>\n<tr>' \
               '<td style="padding-left:2em;padding-right:1em">Selecteer de posts ' \
               '(door ze &eacute;&eacute;n voor &eacute;&eacute;n aan te klikken) die volgens jou het belangrijkst zijn ' \
               'voor voor het topic. Je bepaalt zelf hoeveel posts je selecteert.' \
                '<br><br></td><td style="padding-left:2em;padding-right:1em">' \
                'Als je hieronder de door jou geselecteerde posts leest, kun je checken of je een goede samenvatting van het topic hebt gemaakt. ' \
               'Je kunt een post weer verwijderen uit je selectie door erop te klikken.<br>' \
               'Klik op de \"Verzend selectie\"-knop als je selectie af is. Als je geen enkele post' \
               ' hebt geselecteerd voor dit topic, leg dan in het opmerkingen-veld uit waarom.<br><br>' \
               '</td>'

elif forumtype == "bb":
    instructions = '<td width="33%" style="padding-left:2em;padding-right:1em"><h2>Volledige discussie</h2></td>' \
               '<td width="33%" style="padding-left:2em;padding-right:1em"><h2>Jouw selectie</h2></td></tr>\n<tr>' \
               '<td style="padding-left:2em;padding-right:1em">Selecteer de tekstfragmenten waarvan jij vindt dat ze het ' \
                   'belangrijkst zijn voor de discussie. Je kunt een volledig bericht selecteren (door te klikken op "selecteer ' \
                   'het volledige bericht") of losse zinnen uit het bericht. Je mag zelf bepalen hoeveel berichten en zinnen je ' \
                   'selecteert maar probeer bondig te zijn zodat de samenvatting niet te veel redundante informatie bevat. ' \
                   'De geselecteerde tekstfragmenten zouden samen een informatieve samenvatting van de discussie moeten geven.' \
                '<br><br></td><td style="padding-left:2em;padding-right:1em">' \
                'Je kunt berichten verwijderen uit je suggestie door ze aan te klikken. Je kunt geen losse zinnen verwijderen. ' \
                   'Als je een zin wilt verwijderen, verwijder dan het bericht en selecteer de juist zinnen opnieuw.<br><br>' \
               '</td>'

out.write('<table width="100%">\n<tr  valign="top">'+instructions+'</tr> </table>\n')
outsent.write('<table width="100%">\n<tr  valign="top">'+instructions+'</tr> </table>\n')


out.write('<form name="selected" action="../../../../cgi-bin/show_thread.pl" method="post">\n')
out.write('<div class="col-sm-6">\n')
out.write('<div class="list-group">\n')

outsent.write('<form name="selectedsentences" action="../../../../cgi-bin/show_thread_sent.pl" method="post">\n')
outsent.write('<div class="col-sm-6">\n')
outsent.write('<div class="list-group">\n')


caps = "([A-Z])"
nocaps = "([a-z])"
numbers = "([0-9])"
prefixes = "(Mr|St|Mrs|Ms|Dr)[.]"
suffixes = "(Inc|Ltd|Jr|Sr|Co)"
starters = "(Mr|Mrs|Ms|Dr|He\s|She\s|It\s|They\s|Their\s|Our\s|We\s|But\s|However\s|That\s|This\s|Wherever)"
acronyms = "([A-Z][.][A-Z][.](?:[A-Z][.])?)"
websites = "[.](com|net|org|io|gov)"

if forumtype == "viva":
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
    text = re.sub(numbers+"[.]"+numbers,"\\1<prd>\\2",text) # added by me
    if "Ph.D" in text: text = text.replace("Ph.D.","Ph<prd>D<prd>")
    text = re.sub("\?\) +"+ nocaps,"<qbra> \\1",text) # added by me (question mark followed by closing brackets followed by nocaps
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
    text = re.sub("([;:]-?[\)\(]) +","\\1<stop> ",text) # added by me (emoticons)
    text = re.sub("([\.\?!]+\)?)","\\1<stop>",text)
    if "<stop>" not in text:
        text += "<stop>"
    text = text.replace("<prd>",".")
    text = text.replace("<qbra>","?)")
    text = re.sub('  +',' ',text)
    sents = text.split("<stop>")
    sents = sents[:-1]
    sents = [s.strip() for s in sents]
    return sents

openingpostforthread = dict()
list_of_posts = list()
maxnrofposts = 50
for thread in root:
    threadid = thread.get('id')
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
            if postcount == 1:
                openingpostforthread[threadid] = postid
            postids[postid] = post
            parentid = post.find('parentid').text
            if parentid is not None:
                children_of_parent = list()
                if parentid in children:
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

sentences_per_post = dict()
sentencecount_per_post_array = []
postidperrow = dict()
openingpostwithauthor = ""
def print_post(currentpostid,indent,threadid):
    global row
    global openingpostwithauthor
    global sentences_per_post
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
    row += 1

    sentences = split_into_sentences(bodyofpost)
    sentences_per_post[currentpostid] = sentences
    sentencecount_per_post_array.append(len(sentences))

    sentenced_bodyofpost = ""

    sid = 0
    for sentence in sentences:
        sentenceforclick = re.sub("\'","\\\'",sentence)
        sentenced_bodyofpost += '<a href=\'#\' class="sentence" style=\'text-decoration:none;color:black\'; onclick="addTxt(\''+currentpostid+'_s'+str(sid)+'\',\'selected\');getElementById(\'row'+str(row)+'_s'+str(sid)+'\').innerHTML=\' '+sentenceforclick+'\';return false;" >'+sentence+'</a>&nbsp;'
        sid += 1

    upvotefield = currentpost.find('upvotes')
    downvotefield = currentpost.find('downvotes')

    bodywithauthor = '<b>'+author+'</b> @ '+timestamp+':<br> '+bodyofpost
    #sentenced_bodywithauthor = '<b>'+author+'</b> @ '+timestamp+':<br> '+sentenced_bodyofpost
    sentenced_body = sentenced_bodyofpost

    if openingpostforthread[threadid] == currentpostid:
        openingpostwithauthor = bodywithauthor
        #print openingpostwithauthor

    bodywithauthorforclick = re.sub("\'","\\\'",bodywithauthor)
    #sentencedbodywithauthorforclick = re.sub("\'","\\\'",sentenced_bodywithauthor)
    out.write("<tr>")
    outsent.write("<tr>")
    out.write('<td>')
    outsent.write('<td>')
    if row==1:
        bgcolor="rgb(240,240,240)"
    else:
        bgcolor="white"
    out.write('<a href="#" class="list-group-item" style="background-color:'+bgcolor+'; padding-left:'+str(indent)+'em" ')
    out.write('onclick="addTxt(\''+currentpostid+'\',\'selected\');')
    out.write('getElementById(\'row'+str(row)+'\').innerHTML=\''+str(bodywithauthorforclick.encode('utf-8'))+'\';return false;">')
    out.write(str(bodywithauthor.encode('utf-8')))
    out.write('\n')

    if openingpostforthread[threadid] == currentpostid:
        outsent.write('<a href="#" class="list-group-item" style="background-color:'+bgcolor+'; padding-left:'+str(indent)+'em" ')
        outsent.write('onclick="addTxt(\''+currentpostid+'\',\'selected\');')
        outsent.write('getElementById(\'row'+str(row)+'\').innerHTML=\''+str(bodywithauthorforclick.encode('utf-8'))+'\';return false;">')
        outsent.write(str(bodywithauthor.encode('utf-8'))+"</a>")
    else:
        outsent.write('<a href="#" class="list-group-item" style="background-color:'+bgcolor+'; padding-left:'+str(indent)+'em;" ')
        outsent.write('onclick="addTxt(\''+currentpostid+'\',\'selected\');')
        #outsent.write('getElementById(\'row'+str(row)+'\').innerHTML=\''+str(bodywithauthorforclick.encode('utf-8'))+'\';return false;">'+'<b>'+author+'</b> @ '+timestamp+' '+'<span style="font-size:8pt;float:right;background-color: rgb(153,204,255)">selecteer complete post</span></a>')
        outsent.write('getElementById(\'row'+str(row)+'\').innerHTML=\''+str(bodywithauthorforclick.encode('utf-8'))+'\';return false;">'+'<b>'+author+'</b> @ '+timestamp+' '+'<span style="font-size:8pt;float:right;background-color: rgb(153,204,255)">selecteer het volledige bericht</span></a>')
        outsent.write('<div style="padding-left:'+str(indent)+'em;">'+str(sentenced_body.encode('utf-8'))+'</div>')
    outsent.write('\n')
    postidperrow[row] = currentpostid
    if upvotefield is not None and downvotefield is not None:

        upvotes = currentpost.find('upvotes').text
        downvotes = currentpost.find('downvotes').text
        score = int(upvotes)-int(downvotes)
        out.write('<div style="font-size:8pt;border-style:none">'+str(score)+' likes</div>\n')
        outsent.write('<div style="font-size:8pt;border-style:none;padding-left:'+str(indent)+'em">&nbsp;&nbsp;'+str(score)+' likes</div>\n')

    out.write("</td></tr>\n")
    outsent.write("</td></tr>\n")



def print_children(leaf,indent,threadid): # leaf is a post id, indent is the size of the indentation, row is the nth row of the list
    global row
    indent += 3
    #print indent,leaf
    currentpostid = leaf
    print_post(currentpostid,indent,threadid)

    if leaf in children:
        children_of_leaf = children[leaf]
        #print "has children", children_of_leaf
        for child in children_of_leaf:
            print_children(child,indent,threadid)

#print_children(id_of_firstpost,"")

title=""
noofposts = 0
threadid = ""
for thread in root:
    threadid = thread.get('id')

    category = thread.find('category').text
    if category is None:
        category = ""
    title = thread.find('title').text
    if title is None:
        title = ""
    if title == "" and category == "":
        out.write('<a href="#" class="list-group-item active" style="padding-left:2em"><br><br></a>\n')
        outsent.write('<a href="#" class="list-group-item active" style="padding-left:2em"><br><br> </a>\n')
    else:
        out.write('<a href="#" class="list-group-item active" style="padding-left:2em">[category: '+category+']<br><br>\n<b>'+title+'</b></a>\n')
        outsent.write('<a href="#" class="list-group-item active" style="padding-left:2em">[category: '+category+']<br><br>\n<b>'+title+'</b></a>\n')

    out.write('<table border=1 width="100%">\n')
    outsent.write('<table border=1 width="100%">\n')
    #for posts in thread.findall('posts'):
        #id_of_firstpost = firstpost.get('id')
    id_of_firstpost = list_of_posts[0].get('id')
    noofposts = len(list_of_posts)
    if hierarchy:
        print_children(id_of_firstpost,0,threadid)
    else:
        for post in list_of_posts:
            postid = post.get('id')
            print_post(postid,2,threadid)

    out.write("</table>\n")
    outsent.write("</table>\n")

out.write('</div>\n</div>\n')
outsent.write('</div>\n</div>\n')


out.write('<div class="col-sm-6">\n')
out.write('<div class="list-group">\n')


if title =="" and category=="":
    out.write('<a href="#" class="list-group-item active" style="padding-left:2em"><br><br></a>\n')
else:
    out.write('<a href="#" class="list-group-item active" style="padding-left:2em">[category: '+category+']<br><br>\n<b>'+title+'</b></a>\n')
out.write('<table border=1 width="100%">\n')
out.write("<tr>")
out.write('<td width="100%">')
out.write('<a href="#" class="list-group-item" style="padding-left:2em"  id="row'+str(1)+'">'+str(openingpostwithauthor.encode('utf-8'))+'</a>')
out.write("</td>\n")
out.write("</tr>\n")
for i in range (2,noofposts+1):
    out.write("<tr>")
    out.write('<td width="100%">')
    out.write('<a href="#" class="list-group-item" style="padding-left:2em"  id="row'+str(i)+'" onclick="'
        'addTxt(\'-'+postidperrow[i]+'\',\'selected\');')
    out.write('getElementById(\'row'+str(i)+'\').innerHTML=\''+'...'+'\'">...')
    out.write("</a></td>\n")
    out.write("</tr>\n")
out.write("</table>\n")
out.write('</div>\n</div>\n')

outsent.write('<div class="col-sm-6">\n')
outsent.write('<div class="list-group">\n')
if title =="" and category=="":
    outsent.write('<a href="#" class="list-group-item active" style="padding-left:2em"><br><br></a>\n')
else:
    outsent.write('<a href="#" class="list-group-item active" style="padding-left:2em">[category: '+category+']<br><br>\n<b>'+title+'</b></a>\n')
outsent.write('<table border=1 width="100%">\n')
outsent.write("<tr>")
outsent.write('<td width="100%">')
outsent.write('<a href="#" class="list-group-item" style="padding-left:2em;background-color:rgb(240,240,240);"  id="row'+str(1)+'">'+str(openingpostwithauthor.encode('utf-8'))+'</a>')
outsent.write("</td>\n")
outsent.write("</tr>\n")
for i in range (2,noofposts+1):
    outsent.write("<tr>")
    outsent.write('<td width="100%">')
    outsent.write('<a href="#" class="list-group-item" style="padding-left:2em"  id="row'+str(i)+'" onclick="'
        'addTxt(\'-'+postidperrow[i]+'\',\'selected\');')
    postid = postidperrow[i]
    nrofsentences = len(sentences_per_post[postid])

    sys.stderr.write("\t"+str(nrofsentences)+"\n")
    sentencefillers = ""
    for j in range(0,nrofsentences):
        sentencefillers += "<span id='row"+str(i)+"_s"+str(j)+"'>[...]</span> "
    sentencefillersforclick = re.sub("\'","\\\'",sentencefillers)
    outsent.write('getElementById(\'row'+str(i)+'\').innerHTML=\''+sentencefillersforclick+'\'">'+sentencefillers)

    #
    outsent.write("</a></td>\n")
    outsent.write("</tr>\n")
outsent.write("</table>\n")
outsent.write('</div>\n</div>\n')

avgnrofsentencesperpost = numpy.mean(sentencecount_per_post_array)
#print (avgnrofsentencesperpost)

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
out.write('<br>Opmerkingen (verplicht als je geen enkele post of zin hebt geselecteerd):'
          '<br><input type="text" size="80" name="comments"><br><br>\n')
out.write('<input type="hidden" name="threadid" value="'+threadid+'">\n')
out.write('<input type="hidden" name="forumtype" value="'+forumtype+'">\n')
out.write('<input type="text" id="selected" name="selected" size="40">\n')


if forumtype == "viva" or forumtype == "bb":
    outsent.write('<br>Opmerkingen (verplicht als je geen enkele post of zin hebt geselecteerd):'
          '<br><input type="text" size="80" name="comments"><br><br>\n')
else:
    outsent.write('<br>Comments (required if you did not select any post or sentence):'
          '<br><input type="text" size="80" name="comments"><br><br>\n')

outsent.write('<input type="hidden" name="threadid" value="'+threadid+'">\n')
outsent.write('<input type="hidden" name="forumtype" value="'+forumtype+'">\n')
outsent.write('<input type="hidden" id="selected" name="selected" size="40">\n')

submittext = "Submit selection and go to next thread"
if forumtype == "viva" or forumtype == "bb":
    submittext = "Verzend selectie en ga naar het volgende topic"
out.write('<input type="submit" value="'+submittext+'">\n')
out.write('</form>\n')
outsent.write('<input type="submit" value="'+submittext+'">\n')
outsent.write('</form>\n')

with open("footer.html",'r') as header:
    for line in header:
        out.write(line)
        outsent.write(line)

sys.stderr.write("Output written to "+out.name+"\n")
sys.stderr.write("Output written to "+outsent.name+"\n")

out.close()
outsent.close()

if noofposts < 10:
    os.remove(htmlsentfile)
    os.remove(xmlfile)
    print("Thread has "+str(noofposts)+" posts, removed from sample")

os.remove(htmlfile) # only keep sentenced file
