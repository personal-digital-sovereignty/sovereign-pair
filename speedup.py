from PIL import Image

img = Image.open('docs/assets/demo_video.webp')
frames = []
durations = []

for i in range(img.n_frames):
    img.seek(i)
    frames.append(img.copy())
    durations.append(max(10, int(img.info.get('duration', 70) * 0.2)))

frames[0].save('docs/assets/demo_video.webp', save_all=True, append_images=frames[1:], duration=durations, loop=0)
