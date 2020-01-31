import os
from crowdsorting import app
from crowdsorting import db

APP_ROOT = app.config['APP_ROOT']
APP_DOCS = app.config['APP_DOCS']
ADMIN_PATH = os.path.join(app.config['APP_ROOT'], 'admins.txt')
PM_PATH = os.path.join(app.config['APP_ROOT'], 'projectManagers.txt')

DEFAULT_DESCRIPTION = ""
DEFAULT_SELECTION_PROMPT = "Select the better text"
DEFAULT_PREFERRED_PROMPT = "Better"
DEFAULT_UNPREFERRED_PROMPT = "Worse"
DEFAULT_LANDING_PAGE = "<div class=\"text-center\">" \
                       "<h1>Crowd Sorting</h1>" \
                       "<h2>with the BYU Department of Digital Humanities</h2>" \
                       "<h3>To begin, click on Sorter in the toolbar.</h3>" \
                       "</div>"
DEFAULT_CONSENT_FORM = """
Generic Terms and Conditions Template<br/>
Please read these terms and conditions ("terms", "terms and conditions") carefully before using<br/>
[website] website (the "service") operated by [name] ("us", 'we", "our").<br/>
Conditions of Use<br/>
We will provide their services to you, which are subject to the conditions stated below in this<br/>
document. Every time you visit this website, use its services or make a purchase, you accept the<br/>
following conditions. This is why we urge you to read them carefully.<br/>
Privacy Policy<br/>
Before you continue using our website we advise you to read our privacy policy [link to privacy<br/>
policy] regarding our user data collection. It will help you better understand our practices.<br/>
Copyright<br/>
Content published on this website (digital downloads, images, texts, graphics, logos) is the<br/>
property of [name] and/or its content creators and protected by international copyright laws.<br/>
The entire compilation of the content found on this website is the exclusive property of [name],<br/>
with copyright authorship for this compilation by [name].<br/>
Communications<br/>
The entire communication with us is electronic. Every time you send us an email or visit our<br/>
website, you are going to be communicating with us. You hereby consent to receive<br/>
communications from us. If you subscribe to the news on our website, you are going to receive<br/>
regular emails from us. We will continue to communicate with you by posting news and notices<br/>
on our website and by sending you emails. You also agree that all notices, disclosures,<br/>
agreements and other communications we provide to you electronically meet the legal<br/>
requirements that such communications be in writing.<br/>
Applicable Law<br/>
By visiting this website, you agree that the laws of the [your location], without regard to<br/>
principles of conflict laws, will govern these terms and conditions, or any dispute of any sort that<br/>
might come between [name] and you, or its business partners and associates.<br/>
Disputes<br/>
Any dispute related in any way to your visit to this website or to products you purchase from us<br/>
shall be arbitrated by state or federal court [your location] and you consent to exclusive<br/>
jurisdiction and venue of such courts.<br/>
Comments, Reviews, and Emails<br/>
Visitors may post content as long as it is not obscene, illegal, defamatory, threatening, infringing<br/>
Terms and conditions template by WebsitePolicies.comof intellectual property rights, invasive of privacy or injurious in any other way to third parties.<br/>
Content has to be free of software viruses, political campaign, and commercial solicitation.<br/>
We reserve all rights (but not the obligation) to remove and/or edit such content. When you<br/>
post your content, you grant [name] non-exclusive, royalty-free and irrevocable right to use,<br/>
reproduce, publish, modify such content throughout the world in any media.<br/>
License and Site Access<br/>
We grant you a limited license to access and make personal use of this website. You are not<br/>
allowed to download or modify it. This may be done only with written consent from us.<br/>
User Account<br/>
If you are an owner of an account on this website, you are solely responsible for maintaining the<br/>
confidentiality of your private user details (username and password). You are responsible for all<br/>
activities that occur under your account or password.<br/>
We reserve all rights to terminate accounts, edit or remove content and cancel orders in their<br/>
sole discretion.
"""