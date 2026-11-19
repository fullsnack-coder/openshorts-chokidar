"""Whole-video transcription job, using the dashboard's existing job contract."""
import argparse
import json
import os
import subprocess


def run(source, output):
    from main import transcribe_video, auto_caption_clip, mark_delivery
    from jsonfile import write_json_atomic
    from ffmpeg_utils import video_encode_args, QUALITY_FAST
    os.makedirs(output, exist_ok=True)
    probe = json.loads(subprocess.check_output([
        'ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', source
    ]))
    video = next(s for s in probe['streams'] if s['codec_type'] == 'video')
    duration = float(probe['format']['duration'])
    if duration <= 0:
        raise ValueError('El vídeo no tiene una duración válida.')
    print('🎙️ Transcribiendo el vídeo completo (sin análisis de clips)...', flush=True)
    transcript = transcribe_video(source)
    if not transcript or not transcript.get('segments'):
        raise ValueError('No se detectó voz en el vídeo.')
    clean = os.path.join(output, 'subtitles_clip_1.mp4')
    # Full frame, full duration. Keep a clean copy for subsequent subtitle edits.
    print('🎞️ Preparando el vídeo con el codificador configurado...', flush=True)
    subprocess.run(['ffmpeg', '-nostdin', '-y', '-i', source,
                    '-map', '0:v:0', '-map', '0:a:0?', *video_encode_args(QUALITY_FAST),
                    '-pix_fmt', 'yuv420p',
                    '-c:a', 'aac', '-movflags', '+faststart', clean], check=True)
    clip = {'start': 0, 'end': duration, 'video_title_for_youtube_short': 'Vídeo subtitulado',
            'video_description_for_tiktok': '', 'viral_hook_text': '',
            'width': video['width'], 'height': video['height'], 'subtitles_only': True}
    metadata = {'mode': 'subtitles', 'source_video': os.path.basename(source),
                'output_format': 'original', 'transcript': transcript, 'shorts': [clip]}
    write_json_atomic(os.path.join(output, 'subtitles_metadata.json'), metadata, indent=2)
    captioned = auto_caption_clip(clean, transcript, 0, duration)
    if not captioned:
        raise RuntimeError('No se pudieron generar los subtítulos. Revisa los logs de transcripción y FFmpeg.')
    served = mark_delivery(captioned) if os.environ.get('WATERMARK') == '1' else captioned
    print(f'CLIP_READY 0 {os.path.basename(served)}', flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', required=True)
    parser.add_argument('-o', '--output', required=True)
    args = parser.parse_args()
    run(args.input, args.output)
