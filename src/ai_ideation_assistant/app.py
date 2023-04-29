import streamlit as st
import streamlit_chat
import openai
import numpy as np
import pandas as pd
from PIL import Image

# Has to be the first line
#dosen't work yet
# image = Image.open('C:\Users\ivivi\Desktop\Personal\tum.ai_makethon23\docs\resources\aai-logo.jpg')
# st.image(image)
# st.set_page_config(page_title="Title", page_icon=st.image(Image.open(r'docs/resources/aai-logo-removebg-preview.jpg'), caption='logo'))

st.write("""
# AppliedAI's AI expert is here to help you!
""")
from streamlit_chat import message
message("Hello I'm your digital assistant created by AppliedAI. Together we can find the most suitable AI solution for your problem.")
message("Tell me about your problem.")
message("We are a manufacturer creating break systems that can be integrated in the car wheel. Lately the quality of our parts has dropped and we don't know the reason. Can you help us fix it?", is_user=True)
