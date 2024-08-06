import streamlit as st

video_file = open("https://1726397843.rsc.cdn77.org/live/a8d4dff0-d37a-4f9b-b3a6-a583fb80d31c/video_2.m3u8", 'rb')
video_bytes = video_file.read()

st.video(video_bytes)