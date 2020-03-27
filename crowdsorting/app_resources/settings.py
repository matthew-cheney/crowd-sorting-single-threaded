import os
from crowdsorting import app
from crowdsorting import db

APP_ROOT = app.config['APP_ROOT']
APP_DOCS = app.config['APP_DOCS']
ADMIN_PATH = os.path.join(app.config['APP_ROOT'], 'admins.txt')
PM_PATH = os.path.join(app.config['APP_ROOT'], 'projectManagers.txt')

DEFAULT_TIMEOUT = 30

DEFAULT_DESCRIPTION = ""
DEFAULT_SELECTION_PROMPT = "Select the easier text"
DEFAULT_PREFERRED_PROMPT = "Easier"
DEFAULT_UNPREFERRED_PROMPT = "Harder"
DEFAULT_LANDING_PAGE = """<div class="text-center"><h1>Crowd Sorting</h1><h2>with the BYU Department of Digital Humanities</h2><p><br></p><h2>Please read the following instructions carefully.</h2><p>The
 purpose of this project is to sort Russian texts by 
difficulty. This is typically done by a language professional or 
teacher, who reads each text and arbitrarily assigns a difficulty. 
However, this often does not reflect the actual difficulty language 
learners experience. With your help, we are removing the language 
professional from the equation and annotating this corpus of texts with 
nothing but actual feedback from Russian learners.</p><p>In order to 
accomplish this, we are using pairwise comparisons. Rather than ask you 
to read a text and guess its difficulty, we are simply asking you to 
compare two texts. You will be presented with two relatively short texts
 in Russian. Your task is to read each one and indicate which of the two
 is easier. To be clear - <b>simply pick which of the two texts is easier for you to read.</b><br></p><p>Below are some guidelines for this process. Please read them thoroughly and keep them in mind as you judge text pairs.</p><p><b>1. Read each text carefully.</b><br></p><p>In
 order for us to get valid feedback, you must read both texts. You can 
read one after the other, or switch between them at paragraph or 
sentence breaks. Find a system that works for you, as long as you are 
engaging with both texts.</p><p><b>2. Do not judge on length alone.</b></p><p>Some
 texts are very long, and others are short. This does not necessarily 
indicate difficulty. Think of comparing a short scientific paper to a 
children's chapter book. The book is obviously easier, but it is also 
longer. Do not simply pick the shorter text as the easier one.</p><p><b>3. You do not have to read the entire text.</b></p><p>As
 stated above, some of the texts are very long. For these, you do not 
have to read them entirely. Read enough to get a feel for their 
difficulty, perhaps reading portions from the beginning, middle, and 
end. As long as you give an honest effort to understand each text and 
feel how difficult it is to read, that is enough.</p><p><b>4. Do not take too long or think too much.</b></p><p>We
 are most interested in your first impression. For most pairs, it should
 be apparent after reading several lines which is easier to understand. 
Do not spend a lot of time debating which is harder, or overthinking 
your answer. If two texts seem very close in difficulty, then select 
whichever is easier to read (even marginally) and move on.</p><p><b>5. Use the Too Hard button sparingly.</b></p><p>In
 the upper right corner will be a button labeled "Too Hard." This should
 only be used if you encounter two texts which you flat out cannot 
understand. Think of trying to judge between two texts in Chinese (or 
another language you don't know). You have no way of telling which is 
easier to read, because both are so far above your level. This is the 
only case in which you should use the Too Hard button. <b>DO NOT </b>use this button if two texts are just very close to each other in difficulty.</p><p>Keep
 in mind that you do not have to understand both texts perfectly to tell
 which is harder. This is the advantage of our sorting algorithm. Even 
beginning language learners can often tell which of two texts is easier 
for them to read, without understanding every word. Don't be afraid to 
use the Too Hard button if needed, but try your best to judge between 
every pair.<br></p><p><br></p><p>If you have questions, refer to the Help Section below the sorter or ask your proctor.<br></p><p><br></p><p>You
 will be prompted to agree to our Terms and Conditions on the next page.
 After agreeing once, you will only be asked again if your proctor 
updates them.<br></p><p><br></p><p>Thank you for your participation! 
Once you have read the instructions above, click on Begin Sorting below.
 You may return to the sorter at any time by clicking Sorter in the 
toolbar.<br></p></div>"""

DEFAULT_CONSENT_FORM = """
<h2 align="left">Terms and Conditions</h2><p align="left"><br></p><h5 align="left">Any
 information users provide in the form of judgments between texts while 
participating in this research project can be freely used and 
distributed by the BYU Department of Digital Humanities and others under
 standard open-source licensing. User data such as names and emails are 
stored in this system, but will not be distributed or used beyond 
authentication for this site alone and tracking users to their 
judgments. Users may at any point freely leave the current project. Upon
 doing so, however, the judgments they provided will remain in the 
system, and may still be used as explained above.</h5><h5 align="left"><br></h5><h5 align="left">By clicking on Agree, I certify that I have read and agree to the above terms and conditions.<br></h5>
"""