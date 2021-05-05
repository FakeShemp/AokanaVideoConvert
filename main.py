import os
import subprocess
import UnityPy

TYPES = [
    'VideoClip'
]

ROOT = os.path.dirname(os.path.realpath(__file__))
ASSETS = [os.path.join(ROOT, 'video_ed'), os.path.join(ROOT, 'video_yokoku'), os.path.join(ROOT, 'video_op')]
DST = os.path.join(ROOT, 'StreamingAssets/videoVp8')

IGNOR_DIR_COUNT = 2

os.makedirs(DST, exist_ok=True)


def main():
    for f in ASSETS:
        print(f"Converting {f}")
        src = os.path.realpath(f)
        extract_assets(src)


def extract_assets(src):
    env = UnityPy.load(src)

    for asset in env.assets:
        if not asset.container:
            continue

        cobjs = sorted(((key, obj) for key, obj in asset.container.items(
        ) if obj.type.name in TYPES), key=lambda x: 1 if x[1].type == "Texture2D" else 0)

        for asset_path, obj in cobjs:
            fp = os.path.join(DST, *asset_path.split('/')
            [IGNOR_DIR_COUNT:])
            export_obj(obj, fp)


def export_obj(obj, fp: str, append_name: bool = False) -> list:
    if obj.type not in TYPES:
        return []

    data = obj.read()
    if append_name:
        fp = os.path.join(fp, data.name)

    fp, extension = os.path.splitext(fp)
    os.makedirs(os.path.dirname(fp), exist_ok=True)

    if obj.type == "VideoClip":
        video = data.m_VideoData
        if len(video) == 0:
            pass
        with open(f"{fp}.mp4", "wb") as f:
            f.write(video.tobytes())
        subprocess.run(
            ['ffmpeg', '-i', f"{fp}.mp4", '-max_muxing_queue_size', '500', '-acodec', 'libvorbis', '-qscale:a', '7',
             '-vcodec', 'libvpx', '-pix_fmt', 'yuv420p', '-crf', '0', '-qmin', '0', '-qmax', '15', '-f', 'webm', '-y',
             f"{fp}.webm"])
        os.remove(f"{fp}.mp4")

    return [obj.path_id]


if __name__ == '__main__':
    main()
