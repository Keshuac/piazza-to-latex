from piazza_api import Piazza
import time
import re
import subprocess, os

import sys

def cleanhtml(raw_html):
  cleanr = re.compile('<.*?>')
  cleantext = re.sub(cleanr, '', raw_html)
  return cleantext

def clean(str):
  return  cleanhtml(str.replace('&#43;', '+').replace('&#96;', '`').replace('\\', '\\\\').replace('&#64;', '@').replace('&amp;', '&').replace('&#34;', "''").replace('&#39;', "'").replace('&gt;', "\\textgreater{}").replace('&lt;', "\\textless{}").replace('&', '\\&').replace('#', '\\#').replace('_', '\_').replace('$', '\$').replace('^', '\^{}'))
  
p = Piazza()
p.user_login()
class_id = input("Enter class ID: ")
course_piazza = p.network(class_id)

posts = course_piazza.iter_all_posts()

text = ""
print("Working...")
for post in reversed(list(posts)):
  subject = clean(post['history'][0]['subject'])
  text += "\\section*{" + str(post['nr']) + ": " + subject + "}\n"
  if len(post['children']) > 0:
    text += "\\subsection*{Question}\n"
    text += clean(post['history'][0]['content']) + "\n"
    for child in post['children']:
      if 'history' in child:
        if child['type'] == 's_answer':
          text += "\\subsection*{Student Answer}\n"
          text += clean(child['history'][0]['content']) + "\n" 
        elif child['type'] == 'i_answer':
          text += "\\subsection*{Instructor Answer}\n"
          text += clean(child['history'][0]['content']) + "\n" 
      elif child['type'] == 'followup':
        text += "\\subsection*{Followup}\n"
        text += clean(child['subject']) + "\n" 
        for inner_child in child['children']:
          if inner_child['type'] == 'feedback':
            text += "\\subsubsection*{Feedback}\n"
            text += clean(inner_child['subject']) + "\n" 
  elif 'no_answer' in post and post['no_answer'] == 1:
    text += "\\subsection*{Question}\n"
    text += clean(post['history'][0]['content']) + "\n"
    text += "\\subsection*{**No Answer**}\n"
  elif clean(post['history'][0]['content']) != "":
    text += "\\subsection*{Note}\n"
    text += clean(post['history'][0]['content']) + "\n"
f = open("piazza-export-" + class_id + ".tex", "w+",encoding='utf-8')
f.write("\\documentclass[10pt]{article}\n")
f.write("\\usepackage[utf8]{inputenc}\n")
f.write("\\usepackage[margin=1in]{geometry}\n")
f.write("\\DeclareUnicodeCharacter{00A0}{ }")
f.write("\\title{Piazza Export}\n")
f.write("\\author{Class ID: " + class_id + "}\n")
f.write("\\date{\\today}\n")
f.write("\\begin{document}\n")
f.write("\\maketitle\n")
f.write(text)
f.write("\\end{document}")
f.close()
os.system("pdflatex piazza-export-" + class_id + ".tex")
if sys.platform.startswith('darwin'):
    subprocess.call(('open', "piazza-export-" + class_id + ".pdf"))
elif os.name == 'nt':
    os.system("pdflatex piazza-export-" + class_id + ".pdf")
elif os.name == 'posix':
    subprocess.call(('xdg-open', "piazza-export-" + class_id + ".pdf"))






