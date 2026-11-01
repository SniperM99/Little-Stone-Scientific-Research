from pathlib import Path
import json,base64

def add_action_narration(s):
    rows=json.loads(Path('work/action_narration_manifest.json').read_text())
    clips={x['key']:{'text':x['text'],'src':'data:audio/mpeg;base64,'+base64.b64encode(Path(x['file']).read_bytes()).decode()} for x in rows}
    script='const actionNarrationClips='+json.dumps(clips,ensure_ascii=False)+';\n'+Path('work/action_narration.js').read_text()
    css='''\n#action-narration-panel{margin-top:12px;padding:12px 14px;border-radius:10px;border:1px solid #b4a174;background:#e9dbb4;color:#5c513b}.action-narration-controls{display:flex;align-items:center;gap:8px;flex-wrap:wrap}.action-narration-controls strong{font-size:15px;margin-right:5px}.action-narration-controls button{font-size:13px;padding:5px 10px}.action-narration-controls button:disabled{opacity:.45;cursor:default}#action-narration-toggle[aria-pressed=true]{background:#31574b;color:#fff0bc}#action-narration-status{font-size:14px;line-height:1.65;margin:8px 0 0;color:#5c513b}\n'''
    assert s.count('\nrender();\n</script>')==1
    return s.replace('</style>',css+'</style>').replace('\nrender();\n</script>','\n'+script+'\nrender();\n</script>')
