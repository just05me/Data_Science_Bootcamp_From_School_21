steps = 3
file_name_output = "report"
file_ext = "txt"
report = """
Report

We have made {total} observations from tossing a coin: {tail} of them were tails and {head} of them were heads.  
The probabilities are {fract1:.2f}% and {fract2:.2f}%, respectively.  
Our forecast is that in the next {steps} observations we will have: {ptail} tail and {phead} heads.
"""

file_LOG = "analytics.log"

TG_webhook = "https://api.telegram.org/bot8192548548:AAHQRvZlWx0MzEbyi91wwiakR4lWuJTaqzc/sendMessage"

TG_chat_id = "1563551350"