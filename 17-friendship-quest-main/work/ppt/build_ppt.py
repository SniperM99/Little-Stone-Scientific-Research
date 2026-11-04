from pathlib import Path
import json,re,zipfile
from pptx import Presentation
from pptx.util import Inches,Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.xmlchemy import OxmlElement
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'outputs'
rows=json.loads((ROOT/'work/ten_level_copy.json').read_text())
src=(ROOT/'work/build_ten_levels.py').read_text()
stories=json.loads(re.search(r"stories=(\[.*?\])\n",src)[1].replace("'",'"'))
chapters=['修木桥','拼飞机','守森林','启缆车','建树屋']
themes=['关心与分辨','尊重与接纳','安全与信任','求助与守护','约定与行动']
rewards=['第一块木板装好了！','木桥修好了，一起过河！','机身与双翼安装完成！','飞机拼好了，起飞！','两侧护盾举起来了！','安全小路全部点亮！','缆车电源接通了！','电力充满，缆车到站！','树屋地板搭好了！','树屋建好了，星空亮起来！']
selection=[1,3,4,5,6,7,13,12,14,15]
prs=Presentation(); prs.slide_width=Inches(13.333333);prs.slide_height=Inches(7.5)
BG='F7F1E3';INK='244C43';GOLD='D59B43';MUTED='68786C'; WHITE='FFFFFF'
def rect(sl,x,y,w,h,color,r=False):
 sh=sl.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE if r else MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h));sh.fill.solid();sh.fill.fore_color.rgb=RGBColor.from_string(color);sh.line.fill.background();return sh

def txt(sl,text,x,y,w,h,size=24,color=INK,bold=False):
 sh=sl.shapes.add_textbox(Inches(x),Inches(y),Inches(w),Inches(h));tf=sh.text_frame;tf.word_wrap=True
 tf.margin_left=tf.margin_right=Inches(.03);tf.margin_top=Inches(.03)
 for i,line in enumerate(text.split('\n')):
  p=tf.paragraphs[0] if i==0 else tf.add_paragraph();p.text=line;p.font.name='PingFang SC';p.font.size=Pt(size);p.font.bold=bold;p.font.color.rgb=RGBColor.from_string(color);p.space_after=Pt(10)
 return sh

def base(label):
 sl=prs.slides.add_slide(prs.slide_layouts[6]);sl.background.fill.solid();sl.background.fill.fore_color.rgb=RGBColor.from_string(BG)
 rect(sl,0,0,13.333,.12,INK);txt(sl,'友爱奇旅  /  一年三班',.5,.3,7,.35,13,MUTED);txt(sl,label,9,.3,3.8,.35,13,MUTED)
 txt(sl,'许牧宸 · 10关课堂版',.5,7.12,6,.25,11,MUTED);txt(sl,f'{len(prs.slides):02d}',12.2,7.1,.6,.3,12,MUTED)
 tr=OxmlElement('p:transition');tr.set('advClick','1');sl._element.insert(list(sl._element).index(sl._element.find('{http://schemas.openxmlformats.org/presentationml/2006/main}clrMapOvr'))+1,tr) if sl._element.find('{http://schemas.openxmlformats.org/presentationml/2006/main}clrMapOvr') is not None else sl._element.append(tr)
 return sl

def pic(sl,path,x,y,w,h):
 from PIL import Image
 iw,ih=Image.open(path).size;ratio=iw/ih;target=w/h
 p=sl.shapes.add_picture(str(path),Inches(x),Inches(y),width=Inches(w),height=Inches(h))
 if ratio>target:p.crop_left=p.crop_right=(1-target/ratio)/2
 else:p.crop_top=p.crop_bottom=(1-ratio/target)/2

def note(sl,s):sl.notes_slide.notes_text_frame.text=s

def button(sl,label):
 sh=rect(sl,8.6,6.35,4.1,.48,INK,True);txt(sl,label,8.8,6.39,3.8,.4,15,WHITE,True);return sh

sl=base('五章冒险 · 十次友爱行动');pic(sl,OUT/'友爱奇旅-关卡插图/章节05.jpg',6.9,1.05,5.85,5.8)
txt(sl,'友爱奇旅',.65,1.6,6,1,48,bold=True);txt(sl,'集体为家 · 团结向前',.68,2.85,6,1,27);txt(sl,'修木桥 → 拼飞机 → 守森林\n启缆车 → 建树屋',.68,4.05,6,1.4,23);txt(sl,'一年三班合作闯关 / 主持：许牧宸',.68,6.15,6,.5,18,MUTED)
note(sl,'同学们好，我是许牧宸！今天我们和小梅、科迪一起冒险，五章十关。预计25—30分钟。PPT用翻页揭晓答案，不包含网页小游戏和自动配音。')
sl=base('准备出发');txt(sl,'一起闯关的约定',.7,1,12,.8,38,bold=True)
for i,(a,b) in enumerate([('想回答，先举手','每关请1—2位同学说一说。'),('别人说话，认真听','不同的友善回答，都值得被听见。'),('答错不扣星','可以想一想，也可以请同学帮忙。')]):
 y=2.15+i*1.4;rect(sl,.75,y,11.8,1.15,WHITE,True);txt(sl,f'0{i+1}',1,y+.15,1,.6,30,GOLD,True);txt(sl,a,2.1,y+.08,9,.5,27,bold=True);txt(sl,b,2.1,y+.63,9,.45,18,MUTED)
note(sl,'操作：问题页停下来请同学回答，点击“揭晓参考答案”或按右方向键进入答案页。答案页点击“继续冒险”或按右方向键前进。答案不必逐字一致。学生提到亲身经历时，不当众追问，下课与老师单独交流。')
for c in range(5):
 sl=base(f'第{c+1}章 / {themes[c]}');pic(sl,OUT/f'友爱奇旅-关卡插图/章节{c+1:02d}.jpg',.7,1.15,6.25,5.55)
 txt(sl,f'第{c+1}章',7.4,1.3,5,.5,20,GOLD,True);txt(sl,chapters[c],7.4,2,5,.8,40,bold=True);txt(sl,stories[c],7.4,3.15,5.1,2.8,25);note(sl,stories[c]+'\n章节故事讲完后，进入两道关卡题。')
 for j in range(2):
  i=c*2+j;r=rows[i];imagefile=OUT/f'友爱奇旅-关卡插图/关卡{selection[i]:02d}.jpg'
  for answer in [False,True]:
   sl=base(f'第{i+1:02d}关 / {chapters[c]}');pic(sl,imagefile,.65,1.25,5.45,5.48)
   txt(sl,r['title'],6.5,1.03,6.2,.8,31,bold=True)
   if not answer:
    txt(sl,r['story'],6.5,2.15,6.05,1.65,26);rect(sl,6.45,4.05,6.2,1.65,WHITE,True);txt(sl,r['question'],6.7,4.3,5.75,1.15,29,INK,True)
    b=button(sl,'想好了吗？揭晓参考答案 →');note(sl,f"请1—2位同学回答，给全班思考时间。\n提示：{r['hint']}\n判定：{r['judge']}\n点击后进入答案页。")
   else:
    txt(sl,'参考答案 · 这样说也可以',6.5,2.05,6,.5,18,MUTED)
    txt(sl,'\n'.join(r['answers']),6.5,2.75,6.05,2.1,29,INK,True)
    rect(sl,6.45,5.05,6.2,.93,'E5EBD9',True);txt(sl,rewards[i],6.67,5.22,5.8,.65,21)
    b=button(sl,'继续冒险 →');note(sl,f"判定：{r['judge']}\n口头剧情奖励：{rewards[i]}\n不要求逐字回答。此页用静态剧情奖励代替网页小游戏。")
   # Link added after all slides have been created.
   b.name='NEXT_BUTTON'
sl=base('全班通关');pic(sl,OUT/'友爱奇旅-关卡插图/章节05.jpg',7.3,1.2,5.4,5.6)
txt(sl,'十关完成！',.7,1.15,6.3,.8,42,bold=True);txt(sl,'我们一起读',.7,2.2,6,.5,20,GOLD,True)
txt(sl,'一年三班，像个大家！\n团结友爱，不欺负他！\n遇到危险，离开求助！\n集体为家，团结向前！',.7,3,6.7,3.2,29,bold=True)
note(sl,'木桥、飞机、守护盾、缆车和树屋，都是全班一起完成的。请全班读出约定。安全时可以说“请停止”，危险时先离开、找大人；不能离开时及时呼救。帮助同学不围观、不起哄、不独自对抗。谢谢大家！')
sl=base('把友爱带到明天');txt(sl,'先保护自己，再找大人帮忙',.8,1.3,12,1,39,bold=True)
for k,t in enumerate(['能离开时，先离开危险。','走不开时，大声呼救。','还没解决，就继续找可信赖的大人。']):
 rect(sl,.85,2.7+k*1.05,11.6,.82,WHITE,True);txt(sl,t,1.1,2.85+k*1.05,11,.6,27)
txt(sl,'明天，你准备为同学做哪一件好事？',.9,6.15,11.7,.6,26,GOLD,True)
note(sl,'结束提醒：不要求孩子独自处理推搡或对抗。若有实际经历，课后由老师单独关心与跟进。课件文本及插图来自同目录10关精简版。')
for n,sl in enumerate(prs.slides):
 for sh in sl.shapes:
  if sh.name=='NEXT_BUTTON' and n+1<len(prs.slides):sh.click_action.target_slide=prs.slides[n+1]
path=OUT/'友爱奇旅-10关课堂版.pptx';prs.save(path)
check=Presentation(path)
assert len(check.slides)==29
assert all(s.has_notes_slide for s in check.slides)
assert sum(1 for s in check.slides for sh in s.shapes if sh.name=='NEXT_BUTTON')==20
with zipfile.ZipFile(path) as z:assert z.testzip() is None
print(f'Created and structure-validated: {path}\nSlides: {len(check.slides)}; question/answer pairs: 10; notes: 29')
