from pathlib import Path
from PIL import Image,ImageDraw
import json
m=json.loads(Path('work/character_manifest.json').read_text())
root=Path('outputs/友爱奇旅-关卡插图');root.mkdir(exist_ok=True)
for group in ['levels','chapters']:
    cards=[]
    for x in m[group]:
        im=Image.open(x['path']).convert('RGB')
        im.thumbnail((1200,900) if group=='levels' else (1600,1000))
        dest=root/f"{'关卡' if group=='levels' else '章节'}{x['index']+1:02d}.jpg"
        im.save(dest,quality=87,optimize=True)
        x['local']=str(dest)
        thumb=Image.open(x['path']).convert('RGB');thumb.thumbnail((420,290))
        tile=Image.new('RGB',(440,320),'#f4ead1');tile.paste(thumb,((440-thumb.width)//2,20));ImageDraw.Draw(tile).text((15,302),f"{group} {x['index']+1}",fill='#223d36');cards.append(tile)
    cols=3 if group=='levels' else 2
    contact=Image.new('RGB',(440*cols,320*((len(cards)+cols-1)//cols)),'#102d2d')
    for i,im in enumerate(cards):contact.paste(im,((i%cols)*440,(i//cols)*320))
    contact.save('work/'+group+'-contact.jpg',quality=90)
Path('work/character_manifest.json').write_text(json.dumps(m,ensure_ascii=False))
notes='# 友爱奇旅 · 图片与提示词\n\n使用内置 image_gen 工具制作。十五张关卡图采用《双人成行》的小梅（May）和科迪（Cody）辅助讲述主题；另有五张章节剧情图。图片均已内嵌在 HTML 中，可离线使用。\n\n'
for group,prompts in [('levels','levelPrompts'),('chapters','chapterPrompts')]:
    for x,p in zip(m[group],m[prompts]):notes+=f"## {x['title']}\n\n图片：{x['local']}\n\n最终提示词：\n\n{p}\n\n"
Path('outputs/友爱奇旅-美术说明.md').write_text(notes)
