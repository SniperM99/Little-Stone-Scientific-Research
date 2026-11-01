from pathlib import Path
import json,base64

def add_game_audio(s):
    if 'const voiceClips=' in s:return s
    manifest=json.loads(Path('work/game_audio_manifest.json').read_text())
    clips={kind:{} for kind in ['scene','question','answer','chapter','intro','pledge']}
    for x in manifest:
        clips[x['kind']][str(x['index'])]={'title':x['title'],'src':'data:audio/mpeg;base64,'+base64.b64encode(Path(x['file']).read_bytes()).decode()}
    js='const voiceClips='+json.dumps(clips,ensure_ascii=False)+';\n'+Path('work/game_voice.js').read_text()
    css='''\n#voice-toolbar{display:flex;align-items:center;gap:12px;flex-wrap:wrap;margin:0 0 18px;padding:10px 16px;border:1px solid #a5baa966;border-radius:12px;background:#173e35;color:#f7e7b8}#voice-toolbar>span{font-weight:700}#voice-toolbar small{color:#d0d9c7;font-size:13px}#voice-toolbar button{font-size:14px;padding:7px 12px}#voice-auto[aria-pressed=true]{background:#edcf85;color:#23483b}.voice-panel{margin:14px 0 18px;padding:12px 14px;border:1px solid #9f9f7255;border-radius:12px;background:#e7e4cd55}.voice-actions{display:flex;flex-wrap:wrap;gap:9px}.voice-button{font-size:16px;padding:9px 14px;background:#eae6cd;color:#274a3d;border-color:#91a58a}.voice-controls{display:flex;align-items:center;justify-content:space-between;gap:8px;flex-wrap:wrap;margin-top:10px}.voice-controls span{font-size:12px;opacity:.8}.voice-controls button{font-size:13px;padding:5px 10px;margin-left:6px}.voice-controls button:disabled{opacity:.4;cursor:default}.revealed-answer>.voice-button{margin-top:10px}.chapter-opening-copy .voice-panel{background:#20483f;color:#eee4c8}.hero .voice-panel{max-width:620px}@media(max-width:600px){#voice-toolbar small{width:100%}.voice-button{font-size:15px}.voice-controls{align-items:flex-start}}\n'''
    assert s.count('\nrender();\n</script>')==1
    return s.replace('</style>',css+'</style>').replace('\nrender();\n</script>','\n'+js+'\nrender();\n</script>')

if __name__=='__main__':
    p=Path('outputs/友爱奇旅-微缩冒险闯关游戏.html')
    p.write_text(add_game_audio(p.read_text()))
